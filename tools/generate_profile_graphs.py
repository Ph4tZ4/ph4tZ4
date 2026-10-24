"""Generate README charts from public GitHub data using only Python's standard library."""

import calendar
from collections import Counter
from datetime import date
from html import escape
from html.parser import HTMLParser
import json
import math
from pathlib import Path
import re
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
USERNAME = 'Ph4tZ4'
COLORS = ['#6ee7df', '#60a5fa', '#f6cd6b', '#c4a0ee', '#ef8c97', '#93c97d', '#9eafbc']


class CalendarParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.cells = {}
        self.counts = {}
        self.tooltip = None
        self.text = ''

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'td' and attrs.get('data-date'):
            self.cells[attrs['id']] = attrs['data-date']
        if tag == 'tool-tip':
            self.tooltip = attrs.get('for')
            self.text = ''

    def handle_data(self, data):
        if self.tooltip:
            self.text += data

    def handle_endtag(self, tag):
        if tag == 'tool-tip' and self.tooltip:
            match = re.search(r'\b(No|[\d,]+) contributions?\b', self.text)
            if match:
                count = match[1]
                self.counts[self.tooltip] = 0 if count == 'No' else int(count.replace(',', ''))
            self.tooltip = None

    def days(self):
        # shortcut: GitHub's public calendar HTML is not a versioned API; update this parser if its markup changes.
        if not self.cells or self.cells.keys() - self.counts.keys():
            raise ValueError('Public calendar markup is incomplete; keeping existing charts.')
        return sorted((date.fromisoformat(day), self.counts[key]) for key, day in self.cells.items())


def fetch(url):
    request = urllib.request.Request(url, headers={'User-Agent': 'Ph4tZ4-profile-charts'})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read().decode('utf-8')


def language_counts(repos):
    return Counter(repo['language'] for repo in repos if not repo['fork'] and repo['language'])


def monthly_counts(days):
    counts = Counter()
    for day, count in days:
        counts[day.strftime('%Y-%m')] += count
    return sorted(counts.items())[-12:]


def text(x, y, value, size=16, color='#adbec9', extra=''):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" {extra}>{escape(str(value))}</text>'


def panel(title, subtitle, content, height=320):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="900" height="{height}" '
            f'viewBox="0 0 900 {height}" role="img" aria-labelledby="title desc">'
            f'<title id="title">{escape(title)}</title><desc id="desc">{escape(subtitle)}</desc>'
            f'<rect x="1" y="1" width="898" height="{height - 2}" rx="16" fill="#0b1219" stroke="#263640"/>'
            '<g font-family="Arial, Helvetica, sans-serif">'
            + text(28, 38, title, 23, '#f0f6fa', 'font-weight="700"')
            + text(28, 64, subtitle, 13) + ''.join(content) + '</g></svg>\n')


def languages_chart(counts):
    groups = counts.most_common(6)
    remaining = sum(counts.values()) - sum(value for _, value in groups)
    if remaining:
        groups.append(('Other', remaining))
    total = sum(counts.values())
    content = ['<circle cx="170" cy="185" r="75" fill="none" stroke="#1b2c36" stroke-width="28"/>']
    offset = 0
    for index, (name, count) in enumerate(groups):
        percentage = count / total * 100
        content.append(f'<circle cx="170" cy="185" r="75" fill="none" stroke="{COLORS[index]}" '
                       f'stroke-width="28" pathLength="100" stroke-dasharray="{percentage} {100-percentage}" '
                       f'stroke-dashoffset="{-offset}" transform="rotate(-90 170 185)"/>')
        y = 102 + index * 27
        content += [f'<circle cx="340" cy="{y-5}" r="5" fill="{COLORS[index]}"/>',
                    text(358, y, name, 16, '#f0f6fa'),
                    text(835, y, f'{count} repos / {percentage:.0f}%', 15, extra='text-anchor="end"')]
        offset += percentage
    content += [text(170, 186, total, 32, '#f0f6fa', 'text-anchor="middle" font-weight="700"'),
                text(170, 209, 'repositories', 13, extra='text-anchor="middle"')]
    return panel('Language mix', 'Primary language per public, non-fork repository; not lines of code.', content)


def activity_chart(days):
    months = monthly_counts(days)
    maximum = max(1, max(count for _, count in months))
    content = []
    for fraction in (0, 0.5, 1):
        y = 250 - fraction * 140
        content += [f'<path d="M60 {y}H850" stroke="#263640"/>',
                    text(48, y+5, round(maximum*fraction), 12, extra='text-anchor="end"')]
    points = []
    for index, (month, count) in enumerate(months):
        x = 80 + index * 740 / max(1, len(months)-1)
        y = 250 - count / maximum * 140
        points.append(f'{x:.1f},{y:.1f}')
        label = calendar.month_abbr[int(month[5:])]
        content += [f'<circle cx="{x}" cy="{y}" r="4" fill="#6ee7df"><title>{month}: {count}</title></circle>',
                    text(x, y-13, count, 12, '#f0f6fa', 'text-anchor="middle"'),
                    text(x, 275, label, 12, extra='text-anchor="middle"')]
    content.insert(0, f'<polyline points="{" ".join(points)}" fill="none" stroke="#6ee7df" stroke-width="3"/>')
    return panel('Contribution rhythm', f'Public profile contributions / {months[0][0]} to {months[-1][0]} / current month is partial.', content)


def heatmap_chart(days):
    content = []
    first = days[0][0]
    # Align columns to Sunday, as on GitHub's contribution calendar.
    offset = (first.weekday()+1) % 7
    maximum = max(1, max(count for _, count in days))
    for day, count in days:
        position = (day-first).days + offset
        column, row = divmod(position, 7)
        level = 0 if count == 0 else min(4, max(1, math.ceil(count/maximum*4)))
        color = ['#1b2c36', '#16434c', '#227282', '#35a8ae', '#6ee7df'][level]
        x, y = 58 + column*15, 100 + row*15
        content.append(f'<rect x="{x}" y="{y}" width="11" height="11" rx="2" fill="{color}">'
                       f'<title>{day.isoformat()}: {count} contributions</title></rect>')
        if day.day == 1:
            content.append(text(x, 88, calendar.month_abbr[day.month], 11))
    for label, row in [('Mon', 1), ('Wed', 3), ('Fri', 5)]:
        content.append(text(22, 109 + row*15, label, 10))
    content.append(text(28, 230, f'{sum(count for _, count in days):,} contributions / {days[0][0]} to {days[-1][0]}', 13))
    content.append(text(675, 230, 'Less', 12))
    for index, color in enumerate(['#1b2c36', '#16434c', '#227282', '#35a8ae', '#6ee7df']):
        content.append(f'<rect x="{710+index*18}" y="219" width="12" height="12" rx="2" fill="{color}"/>')
    content.append(text(810, 230, 'More', 12))
    return panel('A year of building', 'Daily contributions visible on my public GitHub profile.', content, 255)


def main():
    parser = CalendarParser()
    parser.feed(fetch(f'https://github.com/users/{USERNAME}/contributions'))
    days = parser.days()
    if (not 300 <= len(days) <= 380 or len({day for day, _ in days}) != len(days)
            or (days[-1][0] - days[0][0]).days + 1 != len(days)):
        raise ValueError('Unexpected calendar range; keeping existing charts.')
    repos = []
    page = 1
    while True:
        batch = json.loads(fetch(f'https://api.github.com/users/{USERNAME}/repos?type=owner&per_page=100&page={page}'))
        if not isinstance(batch, list):
            raise ValueError('Unexpected repository API response.')
        repos.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    charts = {'languages.svg': languages_chart(language_counts(repos)),
              'activity.svg': activity_chart(days), 'contributions.svg': heatmap_chart(days)}
    output = ROOT / 'assets' / 'graphs'
    output.mkdir(exist_ok=True)
    # Fetch and validate all input before replacing any existing images.
    for name, svg in charts.items():
        temporary = output / (name + '.tmp')
        temporary.write_text(svg)
        temporary.replace(output / name)
    print(f'Updated {len(charts)} charts from public GitHub data.')


if __name__ == '__main__':
    main()
