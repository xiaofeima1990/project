# this file is aimed at converting stupid industry company data into a 
# much nicer format of csv file. readable for python
path="E:\\guoxuanma\\DATA\\compay_csv\\"
#path2="E:\\guoxuanma\\DATA\\company2\\"
path3="E:\\guoxuanma\\DATA\\company_geo\\"

path2="G:\\database\\1996-2009csv\\"
path2="G:\\database\\1996-2009dta\\"
path3="G:\\database\\company_geo\\"
data_names=c('2000','2001','2002','2003','2004','2005','2006','2007','2008','2009')

library(readstata13)
library(foreign)

output=function(old_name,new_name,name,temp_df){
  
  
  for (i in c(1:length(old_name))){
    names(temp_df)[i]=new_name[i]
  }
  temp_df <- data.frame(lapply(temp_df, as.character), stringsAsFactors=FALSE)
  for (colname in names(temp_df)) {
    temp_df[[colname]] <- gsub("\t|\n\ |\"", "",temp_df[[colname]])
  }

  write.table(temp_df,file=paste(path3,name,'.txt',sep=''),sep='\t',na='',fileEncoding = 'utf-8',row.names = FALSE)
  
}


#temp=read.csv(paste(path2,'2002.csv',sep='',),header=F)
#temp_df=temp[c(-1),]


# get the candidate geo source data
name='2009'
temp2=read.dta13(paste(path2,name,'.dta',sep=''),convert.factors = FALSE)
x=c(1,2,7,8,3,65)
#temp_df=temp_df[,x]
temp_df=temp2[,x]

## rename the data 

old_name=names(temp_df) ## we can see the names 
## var1 firmID 
## var2 firmName
## var3 districtCode
## var4 prov
## var5 city
## var6 county
## var7 village
## var8 street
## var9 streetAgency
## var10 neighCommittee
## n    ID

new_name=c('firmID','firmName','street','address','districtCode','ID')

#new_name=c('firmID','firmName','districtCode','prov',
#           'city','county','village','street','streetAgency',
#           'neighCommittee','ID')


output(old_name,new_name,name,temp_df)

#write.csv(temp_df,file=paste(path3,'2009.csv',sep=''),fileEncoding = 'gbk',row.names = FALSE)

##--------------------------
## 2004-2008
##--------------------------

## 2008 

## var1 firmName
## var2 districtCode
## var3 prov
## var4 city
## var5 county
## var6 village
## var7 street
## var8 streetAgency
## var9 neighCommittee
## _法人代码 firmID 
## n    ID

name='2008'
temp2=read.dta13(paste(path2,name,'.dta',sep=''),convert.factors = FALSE)
x=c(66,1,6,7,2,67)
temp_df=temp2[,x]

old_name=names(temp_df) ## we can see the names 

#new_name=c('firmID','firmName','districtCode','prov',
#           'city','county','village','street','ID')

new_name=c('firmID','firmName','street','address','districtCode','ID')
output(old_name,new_name,name,temp_df)



## 2007   
name='2007'
temp2=read.dta13(paste(path2,name,'.dta',sep=''),convert.factors = FALSE)
x=c(1,2,8,9,4,142)
temp_df=temp2[,x]

old_name=names(temp_df) ## we can see the names 

#new_name=c('firmID','firmName','districtCode','prov',
#           'city','county','village','street','ID')

new_name=c('firmID','firmName','street','address','districtCode','ID')
output(old_name,new_name,name,temp_df)

## 2006 
name='2006'
temp2=read.dta13(paste(path2,name,'.dta',sep=''),convert.factors = FALSE)
x=c(1,2,8,9,4,138)
temp_df=temp2[,x]

old_name=names(temp_df) ## we can see the names 

#new_name=c('firmID','firmName','districtCode','prov',
#           'city','county','village','street','ID')

new_name=c('firmID','firmName','street','address','districtCode','ID')
output(old_name,new_name,name,temp_df)

## 2005
name='2005'
temp2=read.dta13(paste(path2,name,'.dta',sep=''),convert.factors = FALSE)
x=c(1,2,8,9,4,136)
temp_df=temp2[,x]

old_name=names(temp_df) ## we can see the names 

#new_name=c('firmID','firmName','districtCode','prov',
#           'city','county','village','street','ID')

new_name=c('firmID','firmName','street','address','districtCode','ID')
output(old_name,new_name,name,temp_df)


### 2004
name='2004'
temp2=read.dta13(paste(path2,name,'.dta',sep=''),convert.factors = FALSE)
x=c(1,2,8,9,4,147)
temp_df=temp2[,x]

old_name=names(temp_df) ## we can see the names 

#new_name=c('firmID','firmName','districtCode','prov',
#           'city','county','village','street','ID')

new_name=c('firmID','firmName','street','address','districtCode','ID')
output(old_name,new_name,name,temp_df)

##--------------------------
## 2003
##--------------------------

name='2003'
temp2=read.dta13(paste(path2,name,'.dta',sep=''),convert.factors = FALSE)

x=c(1,2,6,4,5,82)
temp_df=temp2[,x]

## var1 firmID 
## var2 firmName
## var5 address
## var6 street
## var8 districtCode
## var9 countyCode
## n    ID


old_name=names(temp_df) ## we can see the names 

new_name=c('firmID','firmName','street','address','districtCode','ID')

output(old_name,new_name,name,temp_df)



##--------------------------
## 1996-2002
## 各个年份表现不一样 我日
##--------------------------

###1996
name='1996'
temp2=read.dta13(paste(path2,name,'.dta',sep=''),convert.factors = FALSE)
x=c(1,3,7,8,12,158)
temp_df=temp2[,x]
old_name=names(temp_df) ## we can see the names 
new_name=c('firmID','firmName','street','address','districtCode','ID')
output(old_name,new_name,name,temp_df)

### 1997
name='1997'
temp2=read.dta13(paste(path2,name,'.dta',sep=''),convert.factors = FALSE)
x=c(3,4,8,9,13,136)
temp_df=temp2[,x]
old_name=names(temp_df) ## we can see the names 
new_name=c('firmID','firmName','street','address','districtCode','ID')
output(old_name,new_name,name,temp_df)

### 1998
name='1998'
temp2=read.dta13(paste(path2,name,'.dta',sep=''),convert.factors = FALSE)
x=c(1,4,8,9,13,112)
temp_df=temp2[,x]
old_name=names(temp_df) ## we can see the names 
new_name=c('firmID','firmName','street','address','districtCode','ID')
output(old_name,new_name,name,temp_df)


### 1999
name='1999'
temp2=read.dta13(paste(path2,name,'.dta',sep=''),convert.factors = FALSE)
x=c(1,2,6,7,11,110)
temp_df=temp2[,x]
old_name=names(temp_df) ## we can see the names 
new_name=c('firmID','firmName','street','address','districtCode','ID')
output(old_name,new_name,name,temp_df)


### 2000
name='2000'
temp2=read.dta13(paste(path2,name,'.dta',sep=''),convert.factors = FALSE)
x=c(1,2,6,7,11,110)

temp_df=temp2[,x]
old_name=names(temp_df) ## we can see the names 
#new_name=c('firmID','firmName','street','address','districtCode','ID')
new_name=c('firmID','firmName','street','address','districtCode','ID')
output(old_name,new_name,name,temp_df)

### 2001
name='2001'
temp2=read.dta13(paste(path2,name,'.dta',sep=''),convert.factors = FALSE)
x=c(1,2,4,5,8,163)

temp_df=temp2[,x]
old_name=names(temp_df) ## we can see the names 
new_name=c('firmID','firmName','street','address','districtCode','ID')
output(old_name,new_name,name,temp_df)

### 2002
name='2002'
temp2=read.dta13(paste(path2,name,'.dta',sep=''),convert.factors = FALSE)
x=c(1,2,5,6,8,96)

temp_df=temp2[,x]
old_name=names(temp_df) ## we can see the names 
new_name=c('firmID','firmName','street','address','districtCode','ID')
output(old_name,new_name,name,temp_df)

#-----------------------------------------------------------------------------

## this part attempt to use import data into sqlite database
## using sqldf or RSQLite
## using RSQLite
library(readstata13)
library(RSQLite)
path="G:\\database\\1996-2009dta\\"
con <- dbConnect(SQLite(),dbname=paste(path,"industry_company.db",sep=""))

name='2002'
temp=read.dta13(paste(path,name,'.dta',sep=''),convert.factors = FALSE)
dbWriteTable(con, "2002", temp) ## 不行










#-----------------------------------------------------------------------------

library(haven)
write.table(temp_df,file=paste(path3,'2002.txt',sep=''),sep=',',na='',fileEncoding = 'utf-8',row.names = FALSE)
temp_df=data.frame(temp_df,stringsAsFactors = FALSE)
write.dta(temp_df,paste(path3,'2002.dta',sep=''), version = 12L)

xx=read.csv(paste(path3,'2002.txt',sep=''),fileEncoding = 'utf-8')

#temp2=read.dta(paste(path2,'2009.dta',sep=''),convert.factors = FALSE)  