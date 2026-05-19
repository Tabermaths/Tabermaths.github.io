---
layout: page
permalink: /talks/
title: Talks
description: Selected talks, posters, and research presentations
nav: true
nav_order: 4
years: [2026, 2025, 2024, 2022]
---

This page lists selected talks, posters, seminars, and research presentations related to my work on Bayesian imaging, inverse problems, uncertainty quantification, and machine learning.

<!-- _pages/talks.md -->
<div class="publications">

{%- for y in page.years %}
  <h2 class="year">{{y}}</h2>
  {% bibliography -f talks -q @*[year={{y}}]* %}
{% endfor %}

</div>
