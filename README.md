# MirrorLink

Link each vertex to another following a mirror logic to restore mesh symetry if lost.

Add an attribute on mesh.


## Attribute

Name: `pair-id`
Domain: Vertex
Type: Int

|Values|          |   |
|:----:|:--------:|:-:|
|   1+ | pair id  | should exist twice, if more -> overlapping vertices |
|   0  | center   | |x| coordinate < threshold |
|  -1  | unset    | non treated yet |
|  -2  | ignored  | to ignore, for asymetrical vertices of the mesh the user want to ignore |