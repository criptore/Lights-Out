import re, subprocess, sys, pathlib
from PIL import Image
repo = pathlib.Path(sys.argv[1]); out = pathlib.Path(sys.argv[2])
md = (repo/'README.md').read_text(encoding='utf8')
lines = md.splitlines()
title = lines[0].lstrip('# ').strip()
course = lines[2].strip('* ')
members = [l for l in lines[:14] if l.startswith('| ') and not l.startswith('| Name') ]
members = [[c.strip() for c in l.strip('|').split('|')] for l in members]
abstract_md = md[md.index('## Abstract') + len('## Abstract'):md.index('## Table of contents')].strip()
abstract = subprocess.run(['pandoc', '-f', 'markdown', '-t', 'latex'], input=abstract_md, capture_output=True, text=True, check=True).stdout
body = md[md.index('## I. Introduction'):]
body = re.sub(r'^## [IVX]+\. ', '## ', body, flags=re.M)
body = re.sub(r'^### \d+\. ', '### ', body, flags=re.M)
# red "in progress" markers, only for sections that are still unfinished
R = lambda t: '\\textcolor{red}{\\textbf{In progress:} ' + t + '}'
REG = '*Restoration-time regression: in progress.*'
if REG in body:
    body = body.replace('## Evaluation & Analysis\n',
        '## Evaluation & Analysis\n\n' + R('the major-outage classifier results are written; the restoration-time regression results (notebook 03) are still to be added.') + '\n', 1)
    body = body.replace(REG, '### Restoration-time regression\n\n' + R('to be written from notebook 03: models and baselines, final test on unseen storms, feature importance, errors per storm type, and the censoring check.'), 1)
if '## Conclusion: Discussion\n\n*In progress.*' in body:
    body = body.replace('## Conclusion: Discussion\n\n*In progress.*',
        '## Conclusion: Discussion\n\n' + R('to be written: summary of both models, main limits and future work.'), 1)
print('in progress markers:', body.count('textcolor{red}'))
# references: IEEE bibliography instead of a section
refs_tex = ''
if '\n## References\n' in body:
    body, refs_md = body.split('\n## References\n', 1)
    items = [re.match(r'\[(\d+)\] (.+)', p, re.S).groups() for p in re.split(r'\n\s*\n', refs_md.strip())]
    conv = lambda t: subprocess.run(['pandoc', '-f', 'markdown', '-t', 'latex'], input=t, capture_output=True, text=True, check=True).stdout.strip()
    refs_tex = '\\begin{thebibliography}{00}\n' + '\n'.join(f'\\bibitem{{b{n}}} ' + conv(' '.join(t.split())) for n, t in items) + '\n\\end{thebibliography}\n'
    print('references:', len(items))
# add image aspect ratio attribute
def img(m):
    alt, src = m.group(1), m.group(2)
    w, h = Image.open(repo/src).size
    return f'![{alt}]({src}){{ratio={w/h:.2f}}}'
body = re.sub(r'!\[([^\]]*)\]\(([^)]+\.png)\)', img, body)
tex = subprocess.run(['pandoc', '-f', 'markdown-auto_identifiers+pipe_tables', '-t', 'latex', '--shift-heading-level-by=-1', '--no-highlight',
                      '--lua-filter', str(out/'filter.lua')], input=body, capture_output=True, text=True, check=True).stdout
tex = tex.replace('\\tightlist\n', '')
tex = tex.replace('\\begin{verbatim}', '{\\scriptsize\n\\begin{verbatim}').replace('\\end{verbatim}', '\\end{verbatim}}')
def esc(s): return s.replace('&', '\\&').replace('_', '\\_')
authors = '\n\\and\n'.join(
    f'\\IEEEauthorblockN{{{esc(n)}}}\n\\IEEEauthorblockA{{\\textit{{{esc(d)}}}\\\\\n{esc(u)}\\\\\n\\texttt{{{esc(e)}}}}}'
    for n, u, d, e in members)
doc = r'''\documentclass[conference]{IEEEtran}
\IEEEoverridecommandlockouts
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{mathptmx}
\usepackage{graphicx,booktabs,tabularx,array,amsmath,textcomp,xcolor,adjustbox}
\usepackage[hidelinks]{hyperref}
\usepackage{newunicodechar,balance}
\newunicodechar{…}{\ldots}
\newunicodechar{²}{\textsuperscript{2}}
\providecommand{\passthrough}[1]{#1}
\setlength{\emergencystretch}{3em}
\sloppy
\graphicspath{{%s/}}
\begin{document}
\title{%s\thanks{%s}}
\author{
%s
}
\maketitle
\begin{abstract}
\mdseries
%s
\end{abstract}
%s
\balance
%s
\end{document}
''' % (str(repo), esc(title), esc(course), authors, abstract, tex, refs_tex)
(out/'lights-out-ieee.tex').write_text(doc, encoding='utf8')
