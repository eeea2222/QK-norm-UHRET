import sys
f=sys.argv[1]; a=int(sys.argv[2]); b=int(sys.argv[3])
pages=open(f).read().split('\f')
for n in range(a,b+1):
    print(f"\n######## PDF PAGE {n} ########")
    print(pages[n-1])
