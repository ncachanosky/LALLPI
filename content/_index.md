---
# Leave the homepage title empty to use the site title
title:
date: 2022-10-24
type: landing

sections:
  - block: markdown
    content:
      title: 
      text: |
        <div style="text-align: center; font-size: 30px">
            The <b>Latin American Left-Leaning Populism Index</b> (LALLPI) is a measure of active populist regimes in Latin America
        </div>
    
  - block: markdown
    content:
      title: 
      text: |
        <div style="text-align: center; font-size: 30px">
            Coming soon!
        </div>
    design:
      background:
        color: darkorange
        text_color_light: true
  
  - block: collection
    content:
      title: Latest News
      subtitle:
      text:
      count: 5
      filters:
        author: ''
        category: ''
        exclude_featured: false
        publication_type: ''
        tag: ''
      offset: 0
      order: desc
      page_type: post
    design:
      view: card
      columns: '1'

  - block: collection
    content:
      title: Latest Preprints
      text: ""
      count: 5
      filters:
        folders:
          - publication
        publication_type: 'article'
    design:
      view: citation
      columns: '1'

  - block: markdown
    design:
      background:
        image:
          # Add your image background to `assets/media/`.
          filename: C4FE.png
          size: 20%
          position: center
          parallax: false
---
