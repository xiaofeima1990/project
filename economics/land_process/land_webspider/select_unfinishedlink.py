# -*- coding: utf-8 -*-

'''
open the link file 
find the link
save the rest of the link


'''

path='.//url//'

# file_name=input('please input the name of the file yyyy-d.txt')
file_name='2013-11.txt'
fhandle=open(path+file_name,'r')
lines=fhandle.readlines()
fhandle.close()

check='75c72564-ffd9-426a-954b-8ac2df0903b7&recorderguid=f4caa48e-dfc7-49ae-97d2-939cd05513e4'
flag=0
count=0
while flag==0:
	if check in lines[count]:
		flag=1
		break
	count+=1
print("count is ",count)


fhandle=open('unfinished_record_info.txt','w')
fhandle.writelines(lines[count:])
fhandle.close()



