from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

import datetime
import os


def store(_dir, decisions):
    # This is our workaround on how to add additional metadata about the decision
    job_name = os.environ.get("JOB_NAME", "")
    build_url = os.environ.get("BUILD_URL", "")

    for decision in decisions:
        decision["job_name"] = job_name
        decision["build_url"] = build_url
        decision["uploaded"] = datetime.datetime.utcnow().isoformat()

    color_map = {'PASS': '#2222ff', 'FAIL': '#ff2222'}
    # This works for controller because all our metrics are like blah.blah.min, blah.blah.max, blah.blah.iqr etc
    # Not sure if its generic enough though.
    categories = {'.'.join(d['description'].split('.')[:-1]) for d in decisions}
    decisions_by_category = dict()
    methods = list({d['method'] for d in decisions})
    for c in categories:
        if c not in decisions_by_category:
            decisions_by_category[c] = {}
        for m in methods:
            decisions_by_category[c][m] = [d for d in decisions if c in d['description'] and d['method'] == m]
    
    for category in categories:
        for method in decisions_by_category[category].keys():
            pdf = PdfPages(f"{_dir}/{method}_{category}.pdf")
            fig, axs = plt.subplots(nrows=len(decisions_by_category[category][method]), ncols=1, figsize=(20, 30))
            max_i = len(decisions_by_category[category][method])
            for i in range(max_i):
                axs[i].set_title(decisions_by_category[category][method][i]['description'], fontsize=10)
                fig.text(0.5, 0.9, method, horizontalalignment="center")
                violin = axs[i].violinplot(decisions_by_category[category][method][i]['data'])
                axs[i].scatter(y=[decisions_by_category[category][method][i]['value']], x=[1], marker='*', color='black', s=300, zorder=3)
                axs[i].scatter(y=[decisions_by_category[category][method][i]['lower_boundary']], x=[1], marker='.', color='red', s=300, zorder=3)
                axs[i].scatter(y=[decisions_by_category[category][method][i]['upper_boundary']], x=[1], marker='.', color='red', s=300, zorder=3)
                violin['bodies'][0].set_facecolor(color_map[decisions_by_category[category][method][i]['result']])
            pdf.savefig(fig)
            pdf.close()
