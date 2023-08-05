from gmssl import sm3,func
from math import ceil
import random

n=0xFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFF7203DF6B21C6052B53BBF40939D54123
p=0xFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF00000000FFFFFFFFFFFFFFFF
G=(0x32c4ae2c1f1981195f9904466a39c9948fe30bbff2660be1715a4589334c74c7,0xbc3736a2f4f6779c59bdcee36b692153d0a9877cc62a474002df32e52139f0a0)
a=0xFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF00000000FFFFFFFFFFFFFFFC
b=0x28E9FA9E9D9F5E344D5A9E4BCF6509A7F39789F515AB8F92DDBCBD414D940E93

def gcd(m,n): # 最大公因子
    if m%n==0:
        return n
    else:
        return gcd(n,m%n)

def inverse_mod(a,m): # 模逆
    if gcd(a,m)!=1: # 若a和m不互质，则无模逆
        return None 
    x1,x2,x3=1,0,a
    y1,y2,y3=0,1,m
    while y3!=0:
        q=x3//y3 
        y1,y2,y3,x1,x2,x3=(x1-q*y1),(x2-q*y2),(x3-q*y3),y1,y2,y3
    return x1%m

def add(P,Q): # 椭圆曲线加法
    x1,y1=P
    x2,y2=Q
    if x1==y1==0:
        return (x2,y2)
    if x2==y2==0:
        return (x1,y1)
    if x1==x2:
        if y1==y2:
            n=(3*pow(x1,2)+a) # 分子
            m=(2*y1) # 分母
        else:
            return (0,0) # 无穷远点
    else:
        n=y2-y1
        m=x2-x1
        
    la=(n*inverse_mod(m,p))%p
    x3=(pow(la,2)-x1-x2)%p
    y3=(la*(x1-x3)-y1)%p
    return (x3,y3)

def double(point):
    return add(point,point)

def mul(t, point): # 快速乘
    if t==0:
        return 0
    if t==1:
        return point
    if t&1==0:
        return double(mul(t>>1, point))
    if t&1==1:
        return add(point,double(mul(t>>1, point)))

def H(str_): #sm3
    data=bytes.fromhex(str_)
    hash_=sm3.sm3_hash(func.bytes_to_list(data))
    return hash_

def KDF(Z, klen):     
    ct=0x00000001
    v=256  
    Ha=[]
    for i in range(1,ceil(klen/v)+1):  
        Ha.append(H(Z+str(ct).zfill(8)))
        ct+=1
    if klen%v!=0:
        Ha[-1]=Ha[-1][:(klen-v*(klen//v))//4] #最左边的(klen−(v×⌊klen/v⌋))比特
    k = ''.join(Ha)
    return k

def sm2_enc(M, P):
    klen=len(M)*4
    k=random.randint(1,n-1)
    C1=mul(k,G)
    (x1,y1)=C1   
    (x2,y2)=mul(k,P)
    t=KDF(hex(x2)[2:].zfill(64)+hex(y2)[2:].zfill(64),klen)
    if int(t,16)==0:
        print("出错")
        return 
    C2=int(M,16)^int(t,16)
    C3=H(hex(x2)[2:].zfill(64)+M+hex(y2)[2:].zfill(64))
    return (hex(C1[0])[2:].zfill(64),hex(C1[1])[2:].zfill(64)), hex(C2)[2:].zfill(klen//4), C3

def sm2_dec(C,d):
    C1,C2,C3=C
    C1=(int(C1[0],16),int(C1[1],16))
    (x2,y2)=mul(d,C1)
    klen=len(C2)*4
    t=KDF(hex(x2)[2:].zfill(64)+hex(y2)[2:].zfill(64),klen)
    if int(t,16)==0:
        print("出错")
        return 
    M_=int(C2,16)^int(t,16)
    u=H(hex(x2)[2:].zfill(64)+hex(M_)[2:].zfill(klen//4)+hex(y2)[2:].zfill(64))
    if u!=C3:
        print("出错")
        return
    else:
        return hex(M_)[2:].zfill(klen//4)

