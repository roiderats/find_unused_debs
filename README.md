# find_unused_debs
Output list of installed deb packages sorted in last-accessed order, based into access time of all files or symlinks that were installed

Hopefully this is what be what **popcon-largest-unused** is supposed to be. For me, popcon-largest-unused lists 4 texlive-* packages and libjs-jquery-ui-docs. That's just reformatted output of `grep "<OLD>$" /var/log/popularity-contest`.
