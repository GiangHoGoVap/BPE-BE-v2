class CompareProcess:
    name: str
    cycleTime: float
    cost: float
    transparency: dict
    flexibility: float
    exceptionHandling: float
    quality: float

    def __init__(self, **entries):
        self.__dict__.update(entries)


class CompareRequest:
    target: dict
    worst: dict
    as_is: CompareProcess
    to_be: CompareProcess

    def __init__(self, **entries):
        self.__dict__.update(entries)
        print(entries["as_is"], entries["to_be"])
        self.as_is = CompareProcess(**entries["as_is"])
        self.to_be = CompareProcess(**entries["to_be"])


class CompareResponse:
    cycle_time: float
    cost: float
    flexibility: float
    quality: float
    exception_handling: float
    transparency: list

    def __init__(self) -> None:
        self.cycle_time = 0
        self.cost = 0
        self.flexibility = 0
        self.quality = 0
        self.exception_handling = 0
        self.transparency = []


class Compare:
    cycle_time_target: float
    cycle_time_worst: float
    cost_target: float
    cost_worst: float
    flexibility_target: float
    flexibility_worst: float
    quality_target: float
    quality_worst: float
    exception_handling_target: float
    exception_handling_worst: float
    transparency_target: float
    transparency_worst: float

    def config(self, cr: CompareRequest):
        self.flexibility_target = cr.target["flexibility"] if "flexibility" in cr.target else 1
        self.flexibility_worst = cr.worst["flexibility"] if "flexibility" in cr.worst else 0
        self.quality_target = cr.target["quality"] if "quality" in cr.target else 1
        self.quality_worst = cr.worst["quality"] if "quality" in cr.worst else 0
        self.exception_handling_target = cr.target["exceptionHandling"] if "exceptionHandling" in cr.target else 1
        self.exception_handling_worst = cr.worst["exceptionHandling"] if "exceptionHandling" in cr.worst else 0
        self.transparency_target = cr.target["transparency"] if "transparency" in cr.target else 1
        self.transparency_worst = cr.worst["transparency"] if "transparency" in cr.worst else 0
        self.cycle_time_target = cr.target["cycleTime"]
        self.cycle_time_worst = cr.worst["cycleTime"]
        self.cost_target = cr.target["cost"]
        self.cost_worst = cr.worst["cost"]

    def pl(self, current, threshold, target, worst):
        if current > threshold:
            return (current - threshold) / (target - threshold)
        elif current < threshold:
            return (current - threshold) / (threshold - worst)
        return 0

    @classmethod
    def compare(self, cr: dict):
        compare_resquest = CompareRequest(**cr)
        as_is = compare_resquest.as_is
        to_be = compare_resquest.to_be
        # print(compare_resquest.__dict__)
        self.config(self, cr=compare_resquest)
        compare_response = CompareResponse()
        compare_response.cycle_time = self.pl(
            self, to_be.cycleTime, as_is.cycleTime, self.cycle_time_target, self.cycle_time_worst)
        compare_response.cost = self.pl(
            self, to_be.cost, as_is.cost, self.cost_target, self.cost_worst)
        compare_response.flexibility = self.pl(
            self, to_be.flexibility, as_is.flexibility, self.flexibility_target, self.flexibility_worst)
        compare_response.quality = self.pl(
            self, to_be.quality, as_is.quality, self.quality_target, self.quality_worst)
        compare_response.exception_handling = self.pl(
            self, to_be.exceptionHandling, as_is.exceptionHandling, self.exception_handling_target, self.exception_handling_worst)
        for i in to_be.transparency.keys():
            pl_i = {}
            if i not in as_is.transparency:
                pl_i = {
                    "view": to_be.transparency[i]["view"],
                    "pl": 1
                }
            else:
                pl_i = {
                    "view": to_be.transparency[i]["view"],
                    "pl": self.pl(
                        self, to_be.transparency[i]["transparency"], as_is.transparency[i][
                            "transparency"], self.exception_handling_target, self.exception_handling_worst
                    )
                }
            compare_response.transparency.append(pl_i)

        return compare_response
