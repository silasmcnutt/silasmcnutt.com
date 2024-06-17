+++
date = {{ .Date }}
posted-on = {{ .Date }}
draft = false
title = 'Movie Review: {{ .Name | replaceRE "-" " " | title }}'
description = 'A review of the movie {{ .Name | replaceRE "-" " " | title }}.'
weight = 0
series = ["Movie Reviews"]
tags = ["genre", "rating"]
categories = ["movie reviews"]
[params]
  author = 'Silas McNutt'
  rating = 'rating-placeholder'
  movie-title = '{{ .Name | replaceRE "-" " " | title }}'
  year = 'year-placeholder'
  image = 'image-placeholder'
+++

{{< movie-poster >}}

# {{< param movie-title >}} ({{< param year >}}) - {{< star-rating ".Params.rating" >}}

{{< letterboxd >}}
