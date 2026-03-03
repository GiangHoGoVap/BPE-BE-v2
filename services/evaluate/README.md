## Context:

```
in_subprocess:
[
    "${subprocess_id}"
]

# in_subprocess is list of present subprocess (descending level)
# subprocess_id will be removed when it is inactive
```

```
number_of_exception_events:
{
    "${transaction_subprocess_id}": {
        "end_event": ${number of cancel end event},
        "catching_event": ${number of cancel catching event}
    }
}
```

```
list_event_subprocess:
{
	"${code}": {
        "cycle_time": ${total_cycletime},
        "cost": ${total_cost}
    }
}

# code: code of send or receive message
# total_cycletime: total cycle time from sent message to received message
```

```
list_boundary_event:
{
	"${subprocess_id}": {
		"${code}": (${total_cycletime}, ${is_interupting})
	}
}

# subprocess_id: subprocess' id
# code: code of send or receive event
# total_cycletime: total cycle time of boudary event
# is_interupting: type of boundary event
```

## Element:

```
id: id of element
name: name of element
incoming: activities toward element by sequence flow
outgoing: element forwards activities by sequence flow
incoming_messageflow: activities toward element by message flow
outgoing_messageflow: element forwards activities by message flow
type: type of element
className: className in design of element
linkCode: str
cycleTime: cycle time of element
timeDuration: cycle time of timer event
branchingProbabilities: list
taskType: int
eventType: int
isInterrupting: bool
parentId: str
boundary: list
percentage: int
isStart: bool
code: str
```

## Result:

``` 
[
  {
    "name": "Process 1",
    "totalCycleTime": 12,
    "totalCost": 123.000,
    "unitCost": [
    {
      "lane": "Department A",
      "cost": 0.1
    },
    {
      "lane": "Department B",
      "cost": 0.3
    }
    ],
    "transparency": {
      "processA": {
        "view": "Subprocess A",
        "numberOfExplicitTask": 2
      },
      "processB": {
        "view": "Process B",
        "numberOfExplicitTask": 3
      }
    },
    "totalNumberExplicitTasks": 5,
    "quality": 0.345,
    "numberOfOptionalTasks": 12,
    "totalTasks": 24,
    "flexibility": 0.5,
    "handledTasks": 2,
    "unHandledTasks": 3,
    "exceptionHandling": 0.67
  }
]
```