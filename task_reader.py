from collections import defaultdict

import tau_bench.envs.airline.tools as airline_tools
import tau_bench.envs.retail.tools as retail_tools
import tau_bench.envs.telecom.tools as telecom_tools
import tau_bench.envs.telehealth.tools as telehealth_tools

instances = {}
domain = ["airline", "retail", "telecom", "telehealth"]
tools = defaultdict(list)

for d_title, d_tools in zip(domain, [airline_tools, retail_tools, telecom_tools, telehealth_tools]):
    for cls in d_tools.ALL_TOOLS:
        tool = {
            "name": cls.__name__,
            "info": cls.get_info(),
        }
        tools[d_title].append(tool)

with open("tau_bench_tools.json", "w") as f:
    import json
    json.dump(tools, f, indent=4)
    