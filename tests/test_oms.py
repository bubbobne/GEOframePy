import geoframepy.oms_module.oms as oms
import os

#java_home = os.getenv("JAVA_HOME")
#print(java_home)
#  bug I'm into conda geoframe env with java 11 and get false
#print(oms.verify_java_version(java_home))
proj_location = '/home/andreisd/Documents/project/uni/ARTICOLO_KRIGING/simulazioni/benchmark/'
console_location = '/opt/oms-3.6.28-console/'
oms.setup_OMS_project("/opt/miniconda3/envs/geoframe_vincennes/bin/java", proj_location, console_location, verbose=True)
oms.run_simulation("/home/andreisd/Documents/project/uni/ARTICOLO_KRIGING/simulazioni/benchmark/simulation/ERM/vermiglio/1.sim")