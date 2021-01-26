from datetime import date

import jinja2
import pandas as pd
from xhtml2pdf import pisa
from pathlib import Path
import os
from os.path import dirname, abspath

# d = dirname(dirname(abspath(__file__)))
#* jinja2 does NOT support Pathlib
BASEDIR = dirname(os.path.dirname(__file__))
BASEDIR = str(BASEDIR)
print(str(BASEDIR))
df = pd.DataFrame(
    {
        "Average Introducer Score": [9, 9.1, 9.2],
        "Reviewer Scores": ["!!+ ‰+ ‰+ ‰+ ‰: 6, 6, 6", "Something", "Content"],
        "Average Academic Score": [5.7, 5.8, 5.9],
        "Average User Score": [1.2, 1.3, 1.4],
        "Applied for (RC)": [9.2, 9.3, 9.4],
        "Applied for (FEC)": [5.5, 5.6, 5.7],
        "Duration (Months)": [36, 37, 38]
    }
)

#TODO
# # Template invocation:
# return render_template("sales.html", seller_cash=zip(sellers, seller_cash)

# # Jinja2 Loop::
# {% for seller, amount in seller_cash %}
#   <p><strong>{{seller}}: {{amount}}</p>
# {% endfor %}

# With a given base dir, jinja2 will have to look inside a 'templates' folder
html = jinja2.Environment(  # Pandas DataFrame to HTML
    loader=jinja2.FileSystemLoader(str(BASEDIR)+'/templates')).get_template('report_template.html'
                         ).render(date=date.today().strftime('%d, %b %Y'), df=df)

# Convert HTML to PDF
with open(str(BASEDIR) + '/report/report.pdf', "w+b") as out_pdf:
    pisa.CreatePDF(
        src=html,  # HTML to convert
        dest=out_pdf,
        encoding='utf-8'
    )  # File handle to receive result
