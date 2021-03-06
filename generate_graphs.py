import json

import matplotlib
from matplotlib import pyplot
from matplotlib.pyplot import plot

matplotlib.rcParams["figure.dpi"] = 200
matplotlib.rcParams['savefig.dpi'] = 200

# driver_scores_none
# driver_scores_pure

cover = "best_cover_uni_full.json"
f1 = "best_f1_uni_full.json"

every_names = {
    "driver_scores_basic": {
        "name": "Every 100",
        "window": 100
    },
    "driver_scores_every1000": {
        "name": "Every 500",
        "window": 500
    },
    "driver_scores_every16": {
        "name": "Every 8",
        "window": 8
    },
    "driver_scores_every2": {
        "name": "Every Other",
        "window": 1
    },
    "driver_scores_every20": {
        "name": "Every 10",
        "window": 10
    },
    "driver_scores_every4": {
        "name": "Every 2",
        "window": 2
    },
    "driver_scores_every40": {
        "name": "Every 20",
        "window": 20
    },
    "driver_scores_every400": {
        "name": "Every 200",
        "window": 200
    },
    "driver_scores_every8": {
        "name": "Every 4",
        "window": 4
    },
    "driver_scores_every80": {
        "name": "Every 40",
        "window": 40
    },
    "driver_scores_half": {
        "name": "Every 1000",
        "window": 1000
    }
}
random_names = {
    "driver_scores_random": {
        "name": "10 Random",
        "window": 2000 / (1 + 10)
    },
    "driver_scores_random1": {
        "name": "1 Random",
        "window": 2000 / (1 + 1)
    },
    "driver_scores_random1000": {
        "name": "1000 Random",
        "window": 2000 / (1 + 1000)
    },
    "driver_scores_random2": {
        "name": "2 Random",
        "window": 2000 / (1 + 2)
    },
    "driver_scores_random20": {
        "name": "20 Random",
        "window": 2000 / (1 + 20)
    },
    "driver_scores_random200": {
        "name": "200 Random",
        "window": 2000 / (1 + 200)
    },
    "driver_scores_random4": {
        "name": "4 Random",
        "window": 2000 / (1 + 4)
    },
    "driver_scores_random40": {
        "name": "40 Random",
        "window": 2000 / (1 + 40)
    },
    "driver_scores_random400": {
        "name": "400 Random",
        "window": 2000 / (1 + 400)
    },
    "driver_scores_random80": {
        "name": "80 Random",
        "window": 2000 / (1 + 80)
    }
}

methods = [
    "amoc",
    "binseg",
    "bocpd",
    "bocpdms",
    "cpnp",
    "ecp",
    "kcpa",
    "pelt",
    "rfpop",
    "segneigh",
    "wbs",
    "zero",
]

with open(f1) as f1_file:
    f1_data = json.load(f1_file)

with open(cover) as cover_file:
    cover_data = json.load(cover_file)

method_scores = {}

for m in methods:
    f1_scores_fixed = {}
    cover_scores_fixed = {}
    for k, v in every_names.items():
        f1_scores_fixed[v['window']] = {
            'score': f1_data[k][m],
            'name': v['name']
        }
        cover_scores_fixed[v['window']] = {
            'score': cover_data[k][m],
            'name': v['name']
        }
    f1_scores_random = {}
    cover_scores_random = {}
    for k, v in random_names.items():
        f1_scores_random[v['window']] = {
            'score': f1_data[k][m],
            'name': v['name']
        }
        cover_scores_random[v['window']] = {
            'score': cover_data[k][m],
            'name': v['name']
        }
    f1_scores_fixed = sorted(f1_scores_fixed.items(), key=lambda s: s[0])
    cover_scores_fixed = sorted(cover_scores_fixed.items(), key=lambda s: s[0])
    f1_scores_random = sorted(f1_scores_random.items(), key=lambda s: s[0])
    cover_scores_random = sorted(cover_scores_random.items(), key=lambda s: s[0])

    fixed_windows = []
    f1_scores_fixed_y = []
    cover_scores_fixed_y = []
    for i in range(len(f1_scores_fixed)):
        fixed_windows.append(f1_scores_fixed[i][0])
        f1_scores_fixed_y.append(f1_scores_fixed[i][1]['score'])
        cover_scores_fixed_y.append(cover_scores_fixed[i][1]['score'])

    random_windows = []
    f1_scores_random_y = []
    cover_scores_random_y = []
    for i in range(len(f1_scores_random)):
        random_windows.append(f1_scores_random[i][0])
        f1_scores_random_y.append(f1_scores_random[i][1]['score'])
        cover_scores_random_y.append(cover_scores_random[i][1]['score'])

    method_scores[m] = {}
    method_scores[m]['Fixed'] = {}
    method_scores[m]['Fixed']['x'] = fixed_windows
    method_scores[m]['Fixed']['F1'] = f1_scores_fixed_y
    method_scores[m]['Fixed']['Coverage'] = cover_scores_fixed_y
    method_scores[m]['Random'] = {}
    method_scores[m]['Random']['x'] = random_windows
    method_scores[m]['Random']['F1'] = f1_scores_random_y
    method_scores[m]['Random']['Coverage'] = cover_scores_random_y

for window_type in ['Fixed', 'Random']:
    for metric in ['F1', 'Coverage']:
        for m in methods:
            x = method_scores[m][window_type]['x']
            y = method_scores[m][window_type][metric]
            plot(x, y, label=m,)
        pyplot.legend(bbox_to_anchor=(1, 1))
        #pyplot.tight_layout()
        pyplot.xlabel(window_type + " Window Size")
        pyplot.ylabel(metric + " Score")
        pyplot.title(metric + " Score vs " + window_type + " Window Size")
        pyplot.grid()
        pyplot.savefig('graphs/' + window_type + '_window_' + metric + '.png', bbox_inches='tight')
        pyplot.close()
        # pyplot.show()

for window_type in ['Fixed', 'Random']:
    for m in methods:
        pyplot.ylim(0, 1.2)
        for metric in ['F1', 'Coverage']:
            x = method_scores[m][window_type]['x']
            y = method_scores[m][window_type][metric]
            plot(x, y, 'o', label=metric + ' score')
        pyplot.legend(bbox_to_anchor=(1, 1))
        #pyplot.tight_layout()
        pyplot.xlabel(window_type + " Window Size")
        pyplot.ylabel(" Score")
        pyplot.title(" Score vs " + window_type + " Window Size")
        pyplot.grid()
        pyplot.savefig('graphs/' + m + '_' + window_type + '.png', bbox_inches='tight')
        pyplot.close()

print('done')
