# snip

index & search in (snippet-)repos

## features

  - syntax highlighting with pygments (and copy to clipboard directly)
  - pull all repos at once
  - search by keywords and get a preview of the results

## installation (todo...)

  clone this repo
  
      cd snip
      pyvenv-3.4 env
      source env/bin/activate (bash)
      . env/bin/activate.fish (fish)
      pip install -r requirements.txt
  
  then you can clone snippet repos to snip/repos.
  
  snip will index them after a "snip.py pull" (which will pull all repos in snip/repos first) or if you run "snip.py index"
  
## usage

you should set an alias to "snip" (or so) so you dont have to type the whole "python 3 snip search..." thing
 
   alias snip="/home/user/snip/env/bin/python3 /home/user/snip/snip.py"

      
      > snip -h
      usage: snip.py [-h] {pull,show,search,s,index} ...
      
      positional arguments:
        {pull,show,search,s,index}
          pull                pull all repos
          show                show and highlight file
          search (s)          search for a term
          index               re-index all repos
      
      optional arguments:
        -h, --help            show this help message and exit



### todo

  - web frontend (simple template for flask/jinja, "snip web" starts a browser"; rest endpoint for searching (js search thing..))
  - search in github gists (in web view only?)
