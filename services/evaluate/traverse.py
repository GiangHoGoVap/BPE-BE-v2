from .constant import *
from .utils import *
from .elements.gateway import *
from .elements.task import *
from .elements.event import *
from .elements.participant import *
from .elements.sub_process import *


class Traverse:
    def visit(self, e, c: Context, r: Result):
        e.accept(self, c, r)

    def visit_for_NormalTask(self, e: NormalTask, c: Context, r: Result):
        print("Visit task", e.name, e.cycle_time)
        r.steps.append(
            {
                "activity": e.id,
                "cycleTime": e.cycle_time,
                "cost": e.unit_cost * e.cycle_time,
                "label": e.name if e.name else "",
            }
        )

        r.totalTasks += 1
        # r.totalNumberExplicitTasks += 1
        if c.in_xor_block > 0:
            r.numberOfOptionalTasks += 1

        total_cycle_time = e.cycle_time
        total_cost = e.cycle_time * e.unit_cost

        if not len(e.boundary):
            self.visit(e.next[0], c, r)
            r.totalCycleTime += total_cycle_time
            r.totalCost += total_cost
            return

        if type(e.boundary[0]) is TimerEvent:
            max_next_time = 0
            max_next_cost = 0
            for b in e.boundary:
                self.visit(b, c, r)
                max_next_time = max(max_next_time, r.totalCycleTime)
                max_next_cost = max(max_next_cost, r.totalCost)
            if e.boundary[0].is_interrupting:
                r.totalCycleTime = max_next_time
                r.totalCost = max_next_cost
                return

            self.visit(e.next[0], c, r)
            total_cycle_time += r.totalCycleTime
            total_cost += r.totalCost
            r.totalCycleTime = max(total_cycle_time, max_next_time)
            r.totalCost = max(total_cost, max_next_cost)

            # next_time = r.totalCycleTime
            # next_cost = r.totalCost
            # self.handle_for_boundary_timer_event(e, c, r, next_time, next_cost)
            # total_cycle_time += r.totalCycleTime
            # total_cost += r.totalCost
        elif type(e.boundary[0]) is ConditionalEvent:
            self.handle_for_boundary_conditional_event(
                e, e.boundary[0], c, r)

        r.totalCycleTime = total_cycle_time
        r.totalCost = total_cost

    def visit_for_SendTask(self, e: SendTask, c: Context, r: Result):
        print("Visit send task", e.name, e.cycle_time)
        r.steps.append(
            {
                "activity": e.id,
                "cycleTime": e.cycle_time,
                "cost": e.unit_cost * e.cycle_time,
                "label": e.name if e.name else "",
            }
        )

        r.totalTasks += 1
        # r.totalNumberExplicitTasks += 1
        if c.in_xor_block > 0:
            r.numberOfOptionalTasks += 1

        total_cycle_time = e.cycle_time
        total_cost = e.cycle_time * e.unit_cost

        if c.in_loop:
            if isinstance(e.next[0], MessageEvent) and e.next[0].event_type == EventType.INTERMIDIATE_CATCH_EVENT.value:
                self.visit(e.outgoing_messageflow[0], c, r)
            else:
                c.stack_next_send_task.append(e.outgoing_messageflow[0])
                self.visit(e.next[0], c, r)
        else:
            if len(e.outgoing_messageflow) > 0:

                self.visit(e.outgoing_messageflow[0], c, r)
            else:
                self.visit(e.next[0], c, r)

        r.totalCycleTime += total_cycle_time
        r.totalCost += total_cost

    def visit_for_ReceiveTask(self, e: ReceiveTask, c: Context, r: Result):
        print(7)

    def visit_for_NonEvent(self, e: NonEvent, c: Context, r: Result):
        r.totalCycleTime = 0
        r.totalCost = 0
        if e.event_type == EventType.START_EVENT.value:
            print("Visit start event")
            self.visit(e.next[0], c, r)
            return
        elif e.event_type == EventType.END_EVENT.value:
            print("Visit end event")
            return

    def visit_for_MessageEvent(self, e: MessageEvent, c: Context, r: Result):
        print("Visit message event", e.id)
        if e.event_type == EventType.INTERMIDIATE_THROW_EVENT.value:
            if isinstance(e.next[0], ExclusiveGateway) and e.next[0].is_split_gateway():
                c.list_gateway_traveled[e.next[0].id] = e.next[0]

            self.visit(e.outgoing_messageflow[0], c, r)
            if c.in_xor_block > 0:
                next_node = e.next[0]
                if isinstance(next_node, ExclusiveGateway) and next_node.is_join_gateway():
                    gateway_traveled, pre = self.check_exclusive_gateway_traveled(
                        next_node.previous, c)
                    if gateway_traveled:
                        self.visit(e.next[0], c, r)
                    else:
                        return
        elif e.event_type == EventType.INTERMIDIATE_CATCH_EVENT.value:
            if c.in_xor_block > 0 and isinstance(e.next[0], ExclusiveGateway) and e.next[0].is_join_gateway():
                c.stack_next_gateway.append(e.next[0])
                return
            else:
                self.visit(e.next[0], c, r)

        elif e.event_type == EventType.END_EVENT.value:
            if e.code in c.list_event_subprocess:
                # end event triggers a event subprocess
                cycletime_event_subprocess = c.list_event_subprocess[
                    e.code]["cycle_time"]
                cost_event_subprocess = c.list_event_subprocess[e.code]["cost"]
                r.totalCycleTime += cycletime_event_subprocess
                r.totalCost += cost_event_subprocess
            else:
                # end event triggers a boundary event
                r.totalCycleTime = 0
                r.totalCost = 0
        elif e.event_type == EventType.START_EVENT.value:
            if len(e.incoming_messageflow) == 0:
                r.totalCycleTime = 0
                r.totalCost = 0
            self.visit(e.next[0], c, r)
        elif e.event_type == EventType.BOUNDARY_EVENT.value:
            self.visit(e.next[0], c, r)

    def visit_for_TimerEvent(self, e: TimerEvent, c: Context, r: Result):
        print("Visit timer event")
        if not e.time_duration:
            return
        if e.event_type == EventType.INTERMIDIATE_CATCH_EVENT.value:
            self.visit(e.next[0], c, r)
            r.totalCycleTime += e.time_duration
            r.totalCost += e.time_duration * e.unit_cost
            return
        elif e.event_type == EventType.BOUNDARY_EVENT.value:
            r.totalCycleTime = 0
            r.totalCost = 0
            self.visit(e.next[0], c, r)
            r.totalCycleTime += e.time_duration
            r.totalCost += e.time_duration * e.unit_cost
            return
        elif e.event_type == EventType.START_EVENT.value and e.is_interrupting:  # same as standard event
            r.totalCycleTime = 0
            r.totalCost = 0
            self.visit(e.next[0], c, r)
            r.totalCycleTime += e.time_duration
            r.totalCost += e.time_duration * e.unit_cost
            return
        else:  # case start event non-interrupting
            pass

    def visit_for_ErrorEvent(self, e: ErrorEvent, c: Context, r: Result):
        if e.event_type == EventType.START_EVENT.value:
            r.totalCycleTime = 0
            r.totalCost = 0
            self.visit(e.next[0], c, r)
        elif e.event_type == EventType.BOUNDARY_EVENT.value:
            r.totalCycleTime = 0
            r.totalCost = 0
            self.visit(e.next[0], c, r)
        elif e.event_type == EventType.END_EVENT.value:
            if len(c.in_subprocess) > 0:
                c.number_of_exception_events[c.in_subprocess[-1]
                                             ]["throwing_event"] += 1
            if e.code in c.list_event_subprocess:
                # end event triggers a event subprocess
                cycletime_event_subprocess = c.list_event_subprocess[
                    e.code]["cycle_time"]
                cost_event_subprocess = c.list_event_subprocess[e.code]["cost"]
                r.totalCycleTime += cycletime_event_subprocess
                r.totalCost += cost_event_subprocess
            else:
                # end event triggers a boundary event
                r.totalCycleTime = 0
                r.totalCost = 0

    def visit_for_EscalationEvent(self, e: EscalationEvent, c: Context, r: Result):
        print()

    def visit_for_CancelEvent(self, e: CancelEvent, c: Context, r: Result):
        print("Visit cancel event")
        r.totalCycleTime = 0
        r.totalCost = 0
        # must be attached to transaction subprocess
        if e.event_type == EventType.END_EVENT.value:
            if len(c.in_subprocess) > 0:
                c.number_of_exception_events[c.in_subprocess[-1]
                                             ]["throwing_event"] += 1
            if len(c.in_subprocess) > 0:
                c.number_of_exception_events[c.in_subprocess[-1]
                                             ]["end_event"] += 1
            r.totalCycleTime = 0
            r.totalCost = 0
            return
        elif e.event_type == EventType.BOUNDARY_EVENT.value:
            self.visit(e.next[0], c, r)
            return

    def visit_for_SignalEvent(self, e: SignalEvent, c: Context, r: Result):
        print()

    def visit_for_MultipleEvent(self, e: MutipleEvent, c: Context, r: Result):
        print()

    def visit_for_CompensationEvent(self, e: CompensationEvent, c: Context, r: Result):
        print()

    def visit_for_ConditionalEvent(self, e: ConditionalEvent, c: Context, r: Result):
        print("Visit conditional event", e.name)
        if e.event_type in [EventType.INTERMIDIATE_THROW_EVENT.value, EventType.START_EVENT.value,
                            EventType.INTERMIDIATE_CATCH_EVENT.value]:
            temp_result = Result()
            self.visit(e.next[0], c, temp_result)
            r.totalCycleTime += e.percentage * temp_result.totalCycleTime
            r.totalCost += e.percentage * temp_result.totalCost
        elif e.event_type == EventType.BOUNDARY_EVENT.value:
            pass

    def visit_for_LinkEvent(self, e: LinkEvent, c: Context, r: Result):
        pass

    def visit_for_TerminateEvent(self, e: TerminateEvent, c: Context, r: Result):
        print("Visit terminate event")
        r.totalCycleTime = 0
        r.totalCost = 0
        return

    def visit_for_ParallelGateway(self, e: ParallelGateway, c: Context, r: Result):
        c.list_gateway_traveled[e.id] = e

        if e.is_join_gateway():
            if e.id in c.list_gateway:
                c.list_gateway[e.id] += 1
            else:
                c.list_gateway[e.id] = 1 + \
                    self.number_of_gateway_in_nodes(e.previous)
            # check so lan da duyet cua cong join
            if c.list_gateway[e.id] < len(e.previous):
                r.totalCycleTime = 0
                r.totalCost = 0
                return
            print("End parallel gateway")
            r.steps.append(
                {
                    "event": END_PARALLEL_GATEWAY,
                    "gateWay": e.id,
                }
            )
            c.stack_next_gateway.append(e)
            r.totalCycleTime = 0
            r.totalCost = 0
            return
        elif e.is_split_gateway():
            total_cycle_time = 0.0
            total_cost = 0.0
            next_node = None
            print("Start parallel gateway")
            r.steps.append(
                {
                    "event": START_PARALLEL_GATEWAY,
                    "gateWay": e.id,
                }
            )
            for branch in e.next:
                self.visit(branch, c, r)
                branch_cycle_time = r.totalCycleTime
                branch_cost = r.totalCost
                if total_cycle_time < branch_cycle_time:
                    total_cycle_time = branch_cycle_time
                    total_cost = branch_cost
            if len(c.stack_next_gateway) > 0:
                next_node = c.stack_next_gateway.pop().next[0]
            self.visit(next_node, c, r)
            r.totalCycleTime += total_cycle_time
            r.totalCost += total_cost
            return

        r.totalCycleTime = 0
        return

    def visit_for_EventBasedGateway(self, e: EventBasedGateway, c: Context, r: Result):
        print()

    def visit_for_ComplexGateway(self, e: ComplexGateway, c: Context, r: Result):
        print()

    def visit_for_InclusiveGateway(self, e: InclusiveGateway, c: Context, r: Result):
        print()

    def visit_for_ExclusiveGateway(self, e: ExclusiveGateway, c: Context, r: Result):
        c.list_gateway_traveled[e.id] = e

        if e.is_join_gateway():
            self.handle_for_join_exclusive_gateway(e, c, r)
        elif e.is_split_gateway():
            self.handle_for_split_exclusive_gateway(e, c, r)
        return

    def visit_for_Lane(self, e: Lane, c: Context, r: Result):
        print("Visit lane", e.name)

        # Add unit cost of each lane to final result
        if not e.is_visited:
            r.unitCost.append(
                {
                    "lane": e.name,
                    "cost": e.unit_cost
                }
            )
            e.is_visited = True

        for esp in e.event_sub_process:
            self.visit(esp, c, r)
        r.totalCycleTime = 0
        r.totalCost = 0
        if len(e.node) == 0:
            return
        for n in e.node:
            self.visit(n, c, r)

        # r.unitCost.append({
        #     "lane": e.name,
        #     "cost": r.totalCycleTime * e.unit_cost
        # })

    def visit_for_Participant(self, e: Participant, c: Context, r: Result):
        print("Visit participant", e.name)
        total_cycle_time = 0.0
        total_cost = 0.0

        # participant dont have any lane
        if not len(e.lane):
            for esp in e.event_sub_process:
                self.visit(esp, c, r)
            for n in e.node:
                self.visit(n, c, r)

            r.unitCost.append(
                {
                    "lane": e.name,
                    "cost": e.unit_cost
                }
            )

            r.transparency[e.id] = {
                "view": e.name,
                "numberOfExplicitTask": e.number_of_tasks,
                "transparency": (
                    e.number_of_tasks / r.totalNumberExplicitTasks) if r.totalNumberExplicitTasks > 0 else 1
            }
            return

        for l in e.lane:
            self.visit(l, c, r)
            total_cycle_time += r.totalCycleTime
            total_cost += r.totalCost

        for l in e.lane:
            r.transparency[l.id] = {
                "view": l.name,
                "numberOfExplicitTask": l.number_of_tasks,
                "transparency": (
                    l.number_of_tasks / r.totalNumberExplicitTasks) if r.totalNumberExplicitTasks != 0 else 1
            }

        r.totalCycleTime = total_cycle_time
        r.totalCost = total_cost

    def visit_for_EventSubProcess(self, e: EventSubProcess, c: Context, r: Result):
        print("Visit event subprocess")
        r.totalCycleTime = 0
        r.totalCost = 0
        # event subprocess must have one and only one start event
        self.visit(e.node[0], c, r)
        c.list_event_subprocess[e.node[0].code] = {
            "cycle_time": r.totalCycleTime,
            "cost": r.totalCost
        }

    def visit_for_BPESubProcess(self, e: BPESubProcess, c: Context, r: Result):
        print("Visit expanded subprocess")
        self.handle_for_NormalSubProcess(e, c, r)

    def visit_for_TransactionSubProcess(self, e: TransactionSubProcess, c: Context, r: Result):
        print("Visit transaction subprocess")
        self.handle_for_NormalSubProcess(e, c, r)

    def visit_for_CallActivity(self, e: CallActivity, c: Context, r: Result):
        print("Visit call activity")
        self.handle_for_NormalSubProcess(e, c, r)

    def handle_for_NormalSubProcess(self, e: NormalSubProcess, c: Context, r: Result):
        c.in_subprocess.append(e.id)
        c.number_of_exception_events[e.id] = {
            "throwing_event": 0,
            "catching_event": 0
        }

        # traverse all of event sub-processes
        for esp in e.event_sub_process:
            self.visit(esp, c, r)
            if type(esp.node[0]) is ErrorEvent:
                c.number_of_exception_events[e.id]["catching_event"] += 1

        # self.handle_for_all_boundary_SubProcess(e, c, r)

        # traverse start event of subprocess
        subprocess_time, subprocess_cost = self.handle_for_inner_SubProcess(
            e, c, r)
        total_cycle_time = subprocess_time
        total_cost = subprocess_cost

        # if isinstance(e, TransactionSubProcess):
        c.in_subprocess.remove(e.id)

        self.visit(e.next[0], c, r)
        next_time = r.totalCycleTime
        next_cost = r.totalCost

        # all boundary timer events must be traversed
        if len(e.boundary) and type(e.boundary[0]) is TimerEvent:
            self.handle_for_boundary_timer_event(e, c, r, next_time, next_cost)
            total_cycle_time += r.totalCycleTime
            total_cost += r.totalCost

        # case subprocess doesn't have any timer event
        if len(e.boundary) and type(e.boundary[0]) is CancelEvent:
            self.handle_for_boundary_cancel_event(
                e, c, r, next_time, next_cost)
            total_cycle_time += r.totalCycleTime
            total_cost += r.totalCost

        if len(e.boundary) and type(e.boundary[0]) is MessageEvent:
            self.handle_for_boundary_message_event(
                e, c, r, next_time, next_cost)
            total_cycle_time += r.totalCycleTime
            total_cost += r.totalCost

        if len(e.boundary) and type(e.boundary[0]) is ErrorEvent:
            self.handle_for_boundary_error_event(e, c, r, next_time, next_cost)
            total_cycle_time += r.totalCycleTime
            total_cost += r.totalCost

        if c.number_of_exception_events[e.id]["catching_event"] > 0 and c.number_of_exception_events[e.id][
                "throwing_event"] > 0:
            r.handledTasks += 1
        elif c.number_of_exception_events[e.id]["catching_event"] == 0 and c.number_of_exception_events[e.id][
                "throwing_event"] > 0:
            r.unHandledTasks += 1

        r.totalCycleTime = total_cycle_time + next_time
        r.totalCost = total_cost + next_cost

    def handle_for_inner_SubProcess(self, e: NormalSubProcess, c: Context, r: Result):
        # return cycle time of subprocess and list of boundary events cycletime
        subprocess_time = 0.0
        subprocess_cost = 0.0
        # expected subprocess has only one start event
        for se in e.node:
            self.visit(se, c, r)
            subprocess_time += r.totalCycleTime
            subprocess_cost += r.totalCost
        return subprocess_time, subprocess_cost

    def handle_for_boundary_SubProcess(self, e: NormalSubProcess, c: Context, r: Result, class_name: str):
        list_boundary_time = []
        list_boundary_cost = []
        is_interrupting = True

        for b in e.boundary:
            # timer event case take all cycle time of boundary
            if type(b).__name__ == class_name:
                is_interrupting = b.is_interrupting
                self.visit(b, c, r)
                list_boundary_time.append(r.totalCycleTime)
                list_boundary_cost.append(r.totalCost)
                if type(b) is CancelEvent and b.event_type == EventType.BOUNDARY_EVENT.value:
                    c.number_of_exception_events[e.id]["catching_event"] += 1
                if type(b) is ErrorEvent and b.event_type == EventType.BOUNDARY_EVENT.value:
                    c.number_of_exception_events[e.id]["catching_event"] += 1

        return list_boundary_time, list_boundary_cost, is_interrupting

    def handle_for_all_boundary_SubProcess(self, e: NormalSubProcess, c: Context, r: Result):
        for b in e.boundary:
            r.totalCycleTime = 0
            r.totalCost = 0
            self.visit(b, c, r)
            c.list_boundary_event[e.id][b.code] = r.totalCycleTime, r.totalCost, b.is_interupting

    def number_of_gateway_in_nodes(self, node) -> int:
        count = 0
        for i in node:
            if isinstance(i, Gateway):
                count += 1
        return count

    def check_exclusive_gateway_traveled(self, node, c: Context):
        # print("Checking ------->", c.list_gateway_traveled)
        for n in node:
            if type(n) is ExclusiveGateway:
                if n.id not in c.list_gateway_traveled and n.is_split_gateway():
                    return False, n
        return True, None

    def handle_for_loop(self, start: ExclusiveGateway, end: ExclusiveGateway, reloop: float, next_node, c: Context,
                        r: Result):
        self.visit(start.next[0], c, r)

        total_cycle_time = r.totalCycleTime / (1 - reloop)
        total_cost = r.totalCost / (1 - reloop)

        if c.in_loop == 0:
            r.total_loop_probability += reloop
            r.total_loop += 1
        if len(c.stack_next_send_task) > 0:
            self.visit(c.stack_next_send_task.pop(), c, r)
        else:
            self.visit(next_node, c, r)

        r.totalCycleTime += total_cycle_time
        r.totalCost += total_cost

    def handle_for_boundary_conditional_event(self, e: NormalTask, boundary_event: ConditionalEvent, c: Context,
                                              r: Result):
        interrupt = boundary_event.is_interrupting
        percentage = boundary_event.percentage

        task_from_boundary_event = boundary_event.next[0]
        next_task = e.next[0]

        total_cycle_time = e.cycle_time
        total_cost = e.cycle_time * e.unit_cost

        boundary_temp_result = Result()
        seq_temp_result = Result()

        if interrupt:
            c.in_xor_block += 1

        self.visit(task_from_boundary_event, c, boundary_temp_result)
        self.visit(next_task, c, seq_temp_result)

        if interrupt:
            c.in_xor_block -= 1

        boundary_ct = boundary_temp_result.totalCycleTime
        boundary_cost = boundary_temp_result.totalCost
        sequence_ct = seq_temp_result.totalCycleTime
        sequence_cost = seq_temp_result.totalCost

        if interrupt:
            total_cycle_time += percentage * \
                boundary_ct + (1 - percentage) * sequence_ct
            total_cost += percentage * \
                boundary_cost + (1 - percentage) * sequence_cost
        else:
            total_cycle_time += percentage * max(boundary_ct, sequence_ct) + (
                1 - percentage) * sequence_ct
            total_cost += percentage * max(boundary_cost, sequence_cost) + (
                1 - percentage) * sequence_cost
        r.totalCycleTime += total_cycle_time
        r.totalCost += total_cost
        r.numberOfOptionalTasks += boundary_temp_result.numberOfOptionalTasks + \
            seq_temp_result.numberOfOptionalTasks
        r.totalTasks += boundary_temp_result.totalTasks + \
            seq_temp_result.totalTasks

    def handle_for_boundary_timer_event(self, e: NormalTask, c: Context, r: Result, next_time: float, next_cost: float):
        total_cycle_time = 0.0
        total_cost = 0.0
        list_cycle_time_boundary_timer_event, list_cost_boundary_timer_event, is_interrupting = self.handle_for_boundary_SubProcess(
            e, c, r, TimerEvent.__name__)

        if is_interrupting:
            total_cycle_time += max(list_cycle_time_boundary_timer_event)
            total_cost += max(list_cost_boundary_timer_event)
        else:
            total_cycle_time += max(
                max(list_cycle_time_boundary_timer_event), next_time)
            total_cost += max(
                max(list_cost_boundary_timer_event), next_cost)
        r.totalCycleTime = total_cycle_time
        r.totalCost = total_cost

    def handle_for_boundary_cancel_event(self, e: NormalSubProcess, c: Context, r: Result, next_time: float,
                                         next_cost: float):
        total_cycle_time = 0.0
        total_cost = 0.0
        list_cycle_time_boundary_timer_event, list_cost_boundary_timer_event, _ = self.handle_for_boundary_SubProcess(
            e, c, r, CancelEvent.__name__)

        if len(list_cycle_time_boundary_timer_event) > 0:
            total_cycle_time += max(list_cycle_time_boundary_timer_event)
            total_cost += max(list_cost_boundary_timer_event)

        if len(e.boundary) == 0 and not len(list_cycle_time_boundary_timer_event):
            total_cycle_time += next_time
            total_cost += next_cost

        r.totalCycleTime = total_cycle_time
        r.totalCost = total_cost

    def handle_for_boundary_message_event(self, e: NormalSubProcess, c: Context, r: Result, next_time: float,
                                          next_cost: float):
        total_cycle_time = 0.0
        total_cost = 0.0
        list_cycle_time_boundary_timer_event, list_cost_boundary_timer_event, is_interupting = self.handle_for_boundary_SubProcess(
            e, c, r, MessageEvent.__name__)
        if is_interupting:
            total_cycle_time += max(list_cycle_time_boundary_timer_event)
            total_cost += max(list_cost_boundary_timer_event)
        else:
            total_cycle_time += max(max(list_cycle_time_boundary_timer_event),
                                    next_time)
            total_cost += max(max(list_cost_boundary_timer_event),
                              next_cost)
        r.totalCycleTime = total_cycle_time
        r.totalCost = total_cost

    def handle_for_boundary_error_event(self, e: NormalSubProcess, c: Context, r: Result, next_time: float,
                                        next_cost: float):
        total_cycle_time = 0.0
        total_cost = 0.0
        list_cycle_time_boundary_timer_event, list_cost_boundary_timer_event, is_interupting = self.handle_for_boundary_SubProcess(
            e, c, r, ErrorEvent.__name__)
        if is_interupting:
            total_cycle_time += max(list_cycle_time_boundary_timer_event)
            total_cost += max(list_cost_boundary_timer_event)
        else:
            total_cycle_time += max(max(list_cycle_time_boundary_timer_event),
                                    next_time)
            total_cost += max(max(list_cost_boundary_timer_event),
                              next_cost)
        r.totalCycleTime = total_cycle_time
        r.totalCost = total_cost

    def handle_for_join_exclusive_gateway(self, e: ExclusiveGateway, c: Context, r: Result):
        if e.id in c.list_gateway:
            c.list_gateway[e.id] += 1
        else:
            c.list_gateway[e.id] = 1 + \
                self.number_of_gateway_in_nodes(e.previous)

        # Check how many times this join gateway has been visited
        if c.list_gateway[e.id] < len(e.previous):
            r.totalCycleTime = 0
            r.totalCost = 0
            return

        gateway_traveled, pre = self.check_exclusive_gateway_traveled(
            e.previous, c)
        if not gateway_traveled:
            print("Start loop")

            for i, n in enumerate(pre.next):
                if isinstance(n, Gateway) and n == e:
                    reloop = pre.branching_probabilities[i]
                else:
                    next_node = n

            r.steps.append(
                {
                    "event": START_LOOP,
                    "gateWay": e.id,
                    "rework": reloop
                }
            )

            c.in_loop += 1
            c.stack_end_loop.append(pre)

            self.handle_for_loop(e, pre, reloop, next_node, c, r)
            return

        print("End exclusive gateway", e.id)
        r.steps.append(
            {
                "event": END_EXCLUSIVE_GATEWAY,
                "gateWay": e.id,
            }
        )

        if not (len(e.next) > 0 and isinstance(e.next[0], MessageEvent) and e.next[
                0].event_type == EventType.INTERMIDIATE_CATCH_EVENT.value):
            c.stack_next_gateway.append(e)
        r.totalCycleTime = 0
        r.totalCost = 0
        return

    def handle_for_split_exclusive_gateway(self, e: ExclusiveGateway, c: Context, r: Result):
        total_cycle_time = 0.0
        total_cost = 0.0
        if len(c.stack_end_loop) > 0 and len(e.next) == 2 and c.stack_end_loop[-1] == e:
            # If this gateway is an end gateway of a loop
            print("End loop")
            r.steps.append(
                {
                    "event": END_LOOP,
                    "gateway": e.id
                }
            )
            c.in_loop -= 1
            c.stack_end_loop.pop()
            r.totalCycleTime = 0
            r.totalCost = 0
            return
        else:
            # If this gateway start an exclusive block
            print("Start exclusive gateway")
            r.steps.append(
                {
                    "event": START_EXCLUSIVE_GATEWAY,
                    "gateway": e.id,
                    "branchingProbability": e.branching_probabilities
                }
            )

            # if isinstance(e, ExclusiveGateway):
            c.in_xor_block += 1

            for i, branch in enumerate(e.next):
                r.totalCycleTime = 0
                r.totalCost = 0
                self.visit(branch, c, r)
                total_cycle_time += e.branching_probabilities[i] * \
                    r.totalCycleTime
                total_cost += e.branching_probabilities[i] * \
                    r.totalCost

            # if isinstance(e, ExclusiveGateway):
            c.in_xor_block -= 1
            if len(c.stack_next_gateway) > 0:
                next_node = c.stack_next_gateway.pop().next[0]
            else:
                r.totalCycleTime = total_cycle_time
                r.totalCost = total_cost
                return

            self.visit(next_node, c, r)
            r.totalCycleTime += total_cycle_time
            r.totalCost += total_cost
            return
