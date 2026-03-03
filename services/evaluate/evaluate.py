from .traverse import *
from .utils import *
from ..survey_service.survey_result import Survey_result_service


class ProcessDirector:
    map_node_created: dict
    map_element: dict
    linkEventNode: dict

    def __init__(self, map_element):
        self.map_element = map_element
        self.map_node_created = {}
        self.linkEventNode = {}

    def createLinkEventNode(self, instance: LinkEvent, element: Element):
        if instance.linkCode in self.linkEventNode:
            if element.eventType == EventType.INTERMIDIATE_THROW_EVENT.value:
                self.linkEventNode[element.linkCode][0].append(element.id)
            else:
                self.linkEventNode[element.linkCode][1].append(element.id)
        else:
            if element.eventType == EventType.INTERMIDIATE_THROW_EVENT.value:
                self.linkEventNode.update({element.linkCode: [[element.id], []]})
            else:
                self.linkEventNode.update({element.linkCode: [[], [element.id]]})

    def handleLinkEvent(self):
        for linkCode in self.linkEventNode:
            throw_nodes = self.get_node_of_ids(self.linkEventNode[linkCode][0])
            catch_node = self.get_node_of_ids(self.linkEventNode[linkCode][1])[0]

            for throw_node in throw_nodes:
                next_nodes_of_prev_node = throw_node.previous[0].next
                index_of_link_event = next_nodes_of_prev_node.index(throw_node)
                next_nodes_of_prev_node[index_of_link_event] = catch_node.next[0]

                prev_nodes_of_next_node = catch_node.next[0].previous
                try:
                    index_of_link_event = prev_nodes_of_next_node.index(catch_node)
                    prev_nodes_of_next_node[index_of_link_event] = throw_node.previous[
                        0
                    ]
                except:
                    pass

    def create_node(self, element: Element):
        target_class = globals()[element.className]
        instance = target_class(element)

        if isinstance(instance, LinkEvent):
            instance.setAttribute(element.linkCode, element.outgoing, element.incoming)
            self.createLinkEventNode(instance, element)

        if isinstance(instance, ConditionalEvent):
            instance.set_percentage(element.percentage)

        self.map_node_created[element.id] = instance

    def create_node_list(self):
        for id in self.map_element:
            self.map_element[id] = Element(**self.map_element[id])
            self.create_node(self.map_element[id])

    def get_node_of_ids(self, ids: list):
        result = []
        for id in ids:
            result.append(self.map_node_created[id])
        return result

    def build_graph(self):
        self.create_node_list()
        collaboration = None
        for e in self.map_element.values():
            n = self.map_node_created[e.id]
            if isinstance(n, Node):
                n.previous = self.get_node_of_ids(e.incoming)
                n.next = self.get_node_of_ids(e.outgoing)
                n.incoming_messageflow = self.get_node_of_ids(e.incoming_messageflow)
                n.outgoing_messageflow = self.get_node_of_ids(e.outgoing_messageflow)
            elif type(n) is Participant:
                collaboration = self.map_node_created[e.parentID]
                collaboration.participants.append(n)
            elif type(n) is Lane:
                participant = self.map_node_created[e.parentID]
                participant.lane.append(n)

            if isinstance(n, (Task, SubProcess, TimerEvent)):
                parent_object = n
                while not isinstance(parent_object, (Participant, Lane)):
                    parent_element = self.map_element[parent_object.id]
                    parent_object = self.map_node_created[parent_element.parentID]

                n.unit_cost = parent_object.unit_cost
            else:
                pass

            if isinstance(n, Event) and n.event_type == EventType.START_EVENT.value:
                lane = self.map_node_created[e.parentID]
                lane.node.append(n)
            if isinstance(n, Activity) and hasattr(e, "boundary"):
                for b in e.boundary:
                    n.boundary.append(self.map_node_created[b])
            if isinstance(n, EventSubProcess):
                subprocess = self.map_node_created[e.parentID]
                subprocess.event_sub_process.append(n)
        self.handleLinkEvent()

        return collaboration


class Collaboration:
    participants: list
    result: list
    node: list

    def __init__(self, element: Element):
        self.participants = []
        self.result = []
        self.node = []

    def get_total_number_explicit_tasks(self):
        total_number_explicit_tasks = 0
        for p in self.participants:
            if not len(p.lane):
                total_number_explicit_tasks += p.number_of_tasks
            else:
                for l in p.lane:
                    total_number_explicit_tasks += l.number_of_tasks
        return total_number_explicit_tasks


class Evaluate:
    @classmethod
    def evaluate(cls, map_element: dict):
        model = map_element["model"]
        process_version_version = map_element["processVersionVersion"]
        survey_result = Survey_result_service.get_survey_result(process_version_version)
        survey_score = (
            survey_result["totalScore"] if survey_result is not None else None
        )
        collaboration = ProcessDirector(model).build_graph()
        t = Traverse()
        for p in collaboration.participants:
            c = Context()
            r = Result()
            r.name = p.name
            r.totalNumberExplicitTasks = collaboration.get_total_number_explicit_tasks()
            p.accept(t, c, r)
            if r.handledTasks + r.unHandledTasks > 0:
                r.exceptionHandling = r.handledTasks / (
                    r.handledTasks + r.unHandledTasks
                )
            if r.totalTasks > 0:
                r.flexibility = r.numberOfOptionalTasks / r.totalTasks
            if r.total_loop == 0:
                r.quality = 1
            else:
                r.quality = 1 - (r.total_loop_probability / r.total_loop)
            if survey_score is not None:
                r.external_quality = survey_score
                r.total_quality = (r.quality + r.external_quality) / 2
            else:
                r.total_quality = r.quality
            if r.totalCycleTime != 0:
                collaboration.result.append(r)

        return collaboration.result
