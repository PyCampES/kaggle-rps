# RPS Server
1. input:
   - agent_directory
     - each agent in their own {agent}.py file
2. steps:
   1. import each agent function
   2. configure a tournement ALL against ALL
   3. for each run
      1. record the scores
      2. record the log
      3. add to the tournament state



## FastAPI for displaying the result
- Can create a simple html page for it and jinja for displaying the results
- Support displaying the result
- Try to use rich for generating the table
- `docker buildx build --platform=linux/amd64 -f Dockerfile -t kind-registry/test-image:0.0.2 --load .`
