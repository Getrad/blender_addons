import os

rootpath = "X:/projects/chums_season3/anim/_prod/_shotgrid/chums_season3/assets"
#print("rootpath", rootpath)

subpathRIG = "RIG/publish/maya"
#print("subpathRIG", subpathRIG)

atypes = ["Character","Environment","Prop","Proxy"]

for f in atypes:
    #print("f",f)
    typepath = os.path.join(rootpath,f)
    #print("typepath", typepath, os.path.exists(typepath))
    if os.path.exists(typepath):
        theseassets = [f1 for f1 in os.listdir(typepath) if os.path.isdir(os.path.join(typepath,f1))]
        for f2 in theseassets:
            thisassetpath = os.path.join(typepath,f2)
            print(f, f2, thisassetpath)
            thissubpath = os.path.join(thisassetpath, subpathRIG)
            print("    thissubpath", thissubpath, os.path.exists(thissubpath))
            cnt = 0
            if os.path.exists(thissubpath):
                for f3 in os.listdir(thissubpath):
                    if f3.endswith(".ma"):
                        cnt += 1
                        print("    ",f3, os.stat(os.path.join(thissubpath,f3)).st_size)
                print("    ", cnt, " FILES")

