# echoprint-similarity
Compute similarity between a track on Spotify and a local file using Echoprint

Returns a quick overlap metric to check if a local file is the same as a track on Spotify. First pulls the Echoprint string from Spotify's track analysis using their API, then compares the string with a local code on disk (create your own using echoprint-codegen). Useful to see if a track is the same or similar (remix, etc) as one on Spotify.

```
carry:echoprint-similarity bwhitman$ python echoprint_sim.py 
local Running (length 7596) vs remote Running (length 7442) : overlap = 2780 (0.3736)
local Cloudbusting (length 7866) vs remote Cloudbusting (length 7784) : overlap = 2603 (0.3344)
local Running (length 7596) vs remote Cloudbusting (length 7784) : overlap = 123 (0.0158)
local Running (length 7596) vs local Running (length 7596) : overlap = 7596 (1.0000)
local Running (length 7596) vs local Cloudbusting (length 7866) : overlap = 184 (0.0234)
```

