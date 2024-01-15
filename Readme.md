
picsh
=====

Parallel Interactive Cluster Shell, for rapid ad-hoc cluster ops. 

#### Requirements

* Tested on Linux only (Fedora 35, Amazon Linux 2, Ubuntu 18)
* Tested with Python 3.6 and up

#### Features


* Fast interactive shells (re-uses the ssh session)
* Stateful ($cd /var/log followed by $pwd gives you /var/log)
* Ssh to a single node to run full screen curses apps like top
* Browse receive buffers per node
* Keyboard and mouse driven
* Works over ssh so you can put this on a jump host


#### Demo

![picsh demo](https://github.com/carlsborg/carlsborg_media_assets/blob/main/picsh-demo3.gif?raw=true)


#### Setup

* Create a cluster yaml and put it in ~.picsh/cluster_name.yaml. 

Example:  

$ cat .picsh/slurm-dev.yaml

``` 
cluster_name: slurm-dev
login_user: ec2-user
ssh_key_path: /home/ec2-user/.keys/pcluster.pem
nodes:
  - ip: "10.0.27.155"
  - ip: "10.0.25.13"
  - ip: "10.0.23.208"
  - ip: "10.0.31.113"
  - ip: "10.0.18.254"
```


