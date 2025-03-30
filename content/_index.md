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
    content:
      title: Populism by country, 2018
      text: |
        <table>
          <style>
            thead tr {
                background-color: #9F2936;
                color: white;
                font-weight: bold;
                }
         
            .flag {
                width: 30px;
                height: 20px;
                margin-right: 8px;
                vertical-align: middle;
            }

            .country {
                display: flex;
                align-items: center;
                gap: 8px; /* Space between flag and text */
                justify-content: left; /* Center content */
            }

            tbody tr:nth-child(even) {
                background-color: #f9f9f9; /* Light gray for even rows */
            }
          </style>
          <thead>
            <tr>
                <th>Country</th>
                <th>Overall populism</th>
                <th>Economic populism</th>
                <th>Institutional Populism</th>
                <th>Populist rhetoric</th>
            </tr>
          </thead>
          <tbody>
            <tr>
                <td><div class="country"><img src="https://flagcdn.com/w40/ve.png">Venezuela</td></div>
                <td>79.7 (1)</td>
                <td>68.6 (1)</td>
                <td>90.0 (1)</td>
                <td>0.99</td>
            </tr>
            <tr>
                <td><div class="country"><img src="https://flagcdn.com/w40/bo.png">Bolivia</div></td>
                <td>45.2 (2)</td>
                <td>31.6 (3)</td>
                <td>58.8 (3)</td>
                <td>0.87</td>
            </tr>
            <tr>
                <td><div class="country"><img src="https://flagcdn.com/w40/ni.png">Nicaragua</div></td>
                <td>39.8 (3)</td>
                <td>19.6 (4)</td>
                <td>60.0 (2)</td>
                <td>0.69</td>
            </tr>
            <tr>
                <td><div class="country"><img src="https://flagcdn.com/w40/ec.png">Ecuador</div></td>
                <td>38.5 (4)</td>
                <td>34.0 (2)</td>
                <td>42.9 (4)</td>
                <td>0.89</td>
            </tr>
            <tr>
                <td><div class="country"><img src="https://flagcdn.com/w40/sv.png">El Salvador</div></td>
                <td>27.5 (5)</td>
                <td>17.1 (5)</td>
                <td>37.8 (5)</td>
                <td>0.72</td>
            </tr>
            <tr>
                <td><div class="country"><img src="https://flagcdn.com/w40/co.png">Colombia</div></td>
                <td>14.6 (6)</td>
                <td>14.1 (8)</td>
                <td>15.1 (6)</td>
                <td>0.47</td>
            </tr>
            <tr>
                <td><div class="country"><img src="https://flagcdn.com/w40/cr.png">Costa Rica</div></td>
                <td>13.1 (7)</td>
                <td>14.5 (7)</td>
                <td>11.7 (8)</td>
                <td>0.61</td>
            </tr>
            <tr>
                <td><div class="country"><img src="https://flagcdn.com/w40/bb.png">Barbados</div></td>
                <td>11.4 (8)</td>
                <td>14.1 (9)</td>
                <td>8.6 (14)</td>
                <td>0.37</td>
            </tr>
            <tr>
                <td><div class="country"><img src="https://flagcdn.com/w40/uy.png">Uruguay</div></td>
                <td>10.7 (9)</td>
                <td>14.8 (6)</td>
                <td>6.7 (18)</td>
                <td>0.48</td>
            </tr>
            <tr>
                <td><div class="country"><img src="https://flagcdn.com/w40/pa.png">Panama</div></td>
                <td>10.5 (10)</td>
                <td>7.4 (13)</td>
                <td>13.7 (7)</td>
                <td>0.33</td>
            </tr>
            <tr>
                <td><div class="country"><img src="https://flagcdn.com/w40/tt.png">Trinidad y Tobado</div></td>
                <td>9.9 (11)</td>
                <td>11.0 (10)</td>
                <td>8.9 (12)</td>
                <td>0.39</td>
            </tr>
            <tr>
                <td><div class="country"><img src="https://flagcdn.com/w40/br.png">Brazil</div></td>
                <td>8.2 (12)</td>
                <td>7.6 (11)</td>
                <td>8.9 (13)</td>
                <td>0.22</td>
            </tr>
            <tr>
                <td><div class="country"><img src="https://flagcdn.com/w40/jm.png">Jamaica</div></td>
                <td>7.4 (13)</td>
                <td>7.4 (12)</td>
                <td>7.3 (16)</td>
                <td>0.30</td>
            </tr>
            <tr>
                <td><div class="country"><img src="https://flagcdn.com/w40/gt.png">Guatemala</div></td>
                <td>7.3 (14)</td>
                <td>4.3 (15)</td>
                <td>10.2 (9)</td>
                <td>0.18</td>
            </tr>
            <tr>
                <td><div class="country"><img src="https://flagcdn.com/w40/do.png">Dominican Republic</div></td>
                <td>6.5 (15)</td>
                <td>3.6 (18)</td>
                <td>9.32 (10)</td>
                <td>0.13</td>
            </tr>
            <tr>
                <td><div class="country"><img src="https://flagcdn.com/w40/py.png">Paraguay</div></td>
                <td>6.2 (16)</td>
                <td>3.9 (17)</td>
                <td>8.5 (15)</td>
                <td>0.15</td>
            </tr>
            <tr>
                <td><div class="country"><img src="https://flagcdn.com/w40/ar.png">Argentina</div></td>
                <td>6.2 (17)</td>
                <td>6.3 (14)</td>
                <td>6.0 (19)</td>
                <td>0.17</td>
            </tr>
            <tr>
                <td><div class="country"><img src="https://flagcdn.com/w40/mx.png">Mexico</div></td>
                <td>5.5 (18)</td>
                <td>4.0 (16)</td>
                <td>7.0 (16)</td>
                <td>0.14</td>
            </tr>
            <tr>
                <td><div class="country"><img src="https://flagcdn.com/w40/hn.png">Honduras</div></td>
                <td>2.6 (19)</td>
                <td>1.4 (20)</td>
                <td>3.7 (20)</td>
                <td>0.06</td>
            </tr>
            <tr>
                <td><div class="country"><img src="https://flagcdn.com/w40/cl.png">Chile</div></td>
                <td>2.4 (20)</td>
                <td>3.0 (19)</td>
                <td>1.8 (21)</td>
                <td>0.15</td>
            </tr>
          </tbody>
        </table>

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
