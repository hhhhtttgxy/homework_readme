import time
import random
from func import *

n=0xFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFF7203DF6B21C6052B53BBF40939D54123
p=0xFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF00000000FFFFFFFFFFFFFFFF
G=(0x32c4ae2c1f1981195f9904466a39c9948fe30bbff2660be1715a4589334c74c7,0xbc3736a2f4f6779c59bdcee36b692153d0a9877cc62a474002df32e52139f0a0)
a=0xFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF00000000FFFFFFFFFFFFFFFC
b=0x28E9FA9E9D9F5E344D5A9E4BCF6509A7F39789F515AB8F92DDBCBD414D940E93

def ECDSA_keygenerate(): #公私钥
    dA=random.randint(1,n-1)
    QA=mul(dA,G)
    return dA,QA
    
def ECDSA_sign(m,dA): # 签名
    z=H(m.hex())
    z=int(z,16)
    while True:
        k=random.randint(1,n-1)
        x1,_=mul(k,G)
        r=x1%n
        s=(inverse_mod(k,n)*(z+r*dA))%n
        if r!=0 and s!=0:
            return r,s

def ECDSA_verify(m,r,s,QA): # 验签
    if r<1 or r>n-1 or type(r)!=int or s<1 or s>n-1 or type(s)!=int:
        return False
    z=H(m.hex())
    z=int(z,16)
    inverse_s=inverse_mod(s,n)
    u1=(z*inverse_s)%n
    u2=(r*inverse_s)%n
    x1,_=add(mul(u1,G),mul(u2,QA))
    return r%n==x1%n

#2
def ECDSA_sign_2(m,dA,k): # 签名
    z=H(m.hex())
    z=int(z,16)
    x1,_=mul(k,G)
    r=x1%n
    s=(inverse_mod(k,n)*(z+r*dA))%n
    if r!=0 and s!=0:
        return r,s
        
def ECDSA_pitfall_2(m1,m2,r,s1,s2):
    z1=H(m1.hex())
    z1=int(z1,16)
    z2=H(m2.hex())
    z2=int(z2,16)
    d=((s2*z1-s1*z2)*inverse_mod(r*(s1-s2),n))%n
    return d
    
if __name__ == "__main__":
    m1=b"Hello Friend!"
    m2=b"Hi Bro"
    dA,QA=ECDSA_keygenerate()
    print("私钥：{}".format(dA))
    k=random.randint(1,n-1)
    r1,s1=ECDSA_sign_2(m1,dA,k)
    r2,s2=ECDSA_sign_2(m2,dA,k)
    start_time = time.time()
    d=ECDSA_pitfall_2(m1,m2,r1,s1,s2)
    end_time = time.time()
    print("解出的私钥：{}".format(d))
    if d==dA:
        print("一致")
    print("用时：{}秒".format(end_time - start_time))
