import pandas as pd

from datetime import datetime

with open("config_wirenumbers", 'r', encoding='utf8') as f:
    conf = f.readlines()
#more to do:
#1. auto duplicate XB terminals with :WH connection points

old_file= conf[0].lstrip('old_filename:').rstrip('\n')
df = pd.read_excel(old_file)
temp = pd.DataFrame() 

############# 1. duplicate data, get source and target swapped for the second part of data  VVVVVVVVVVV
temp[['Source','Source location','Target','Target location']] = df[['Target','Target location','Source','Source location']]
df2 = pd.concat([df,temp])
df2.reset_index(inplace=True)
with open("log", 'a', encoding='utf8') as f:
    f.write(datetime.now().strftime("%D   %H:%M:%S") + "\tRead data source: " + old_file+ "\n")
    f.write(datetime.now().strftime("%D   %H:%M:%S") + "\tSwapped target and source, and append to the end." + "\n")

############# 2. pick double ":" in terminals, delete data after the second ":", together with the :    VVVVVVVVVVV

filt2 = (df2['Source'].str.count(':') > 1) & (df2['Source'].str.contains('-XB')) & ((df2['Source'].str.endswith(':a')) | (df2['Source'].str.endswith(':b')))
df2.loc[filt2, 'Source'] = df2.loc[filt2,'Source'].str.removesuffix(':a')   #delete :a terminal connection points
df2.loc[filt2, 'Source'] = df2.loc[filt2,'Source'].str.removesuffix(':b')   #delete :b terminal connection points

filt2 = (df2['Source'].str.count(':') > 1)  & (df2['Source'].str.contains('-XB')) & (df2['Source'].str.endswith(':1'))
df2.loc[filt2, 'Source'] = df2.loc[filt2,'Source'].str.removesuffix(':1')

filt2 = (df2['Source'].str.count(':') > 1)  & (df2['Source'].str.contains('-XB')) & (df2['Source'].str.endswith(':2'))
df2.loc[filt2, 'Source'] = df2.loc[filt2,'Source'].str.removesuffix(':2')

filt2 = (df2['Source'].str.count(':') > 1)  & (df2['Source'].str.contains('-XB')) & (df2['Source'].str.endswith(':3'))
df2.loc[filt2, 'Source'] = df2.loc[filt2,'Source'].str.removesuffix(':3')

filt2 = (df2['Source'].str.count(':') > 1)  & (df2['Source'].str.contains('-XB')) & (df2['Source'].str.endswith(':4'))
df2.loc[filt2, 'Source'] = df2.loc[filt2,'Source'].str.removesuffix(':4')

filt2 = (df2['Source'].str.count(':') > 1)  & (df2['Source'].str.contains('-XB')) & (df2['Source'].str.endswith(':5'))
df2.loc[filt2, 'Source'] = df2.loc[filt2,'Source'].str.removesuffix(':5')

with open("log", 'a', encoding='utf8') as f:
    f.write(datetime.now().strftime("%D   %H:%M:%S")+ "\tDeleted terminal connection point designations" + "\n")

# print(df2.loc[df2['Source'] == "'=1FT1.12.6+CAB2-TA1:OutDC:-''", 'Source'])
############# 3. delete all "SH" or "PE", or any wire number with '=+' wire numbers      VVVVVVVVVVV

filt2 = (df2['Source'].str.contains('SH') | df2['Source'].str.contains('PE') | (df2['Source'].str.len()< 9 ) | df2['Target'].str.contains('SH') | df2['Target'].str.contains('PE'))       #delete PE, SH and =+xx
df2.drop(df2[filt2].index, inplace=True)
with open("log", 'a', encoding='utf8') as f:
    f.write(datetime.now().strftime("%D   %H:%M:%S") + "\tDeleted wire numbers with 'PE' or 'SH'" + "\n")
 

# print(df2.loc[df2['Source'] == "'=1FT1.12.6+CAB2-TA1:OutDC:-''", 'Source'])
############# 4. delete duplicated wire numbers, not for terminals      VVVVVVVVVVV    ???????????

# filt2 = df2['Source'].str.contains("XB")
# df_t = df2.loc[filt2]       #759 pcs, terminals
# df2 = df2.loc[~filt2]       #1515 pcs, not terminals
# df2.drop(df2[df2['Source'].duplicated()].index, inplace = True)     #???
# df2 = pd.concat([df2,df_t])

#############  5. delete all the wire numbers at cable plug side
lines_2_delete = conf[1].lstrip('lines to delete:').rstrip('\n').split(",")
filt_2_delete = False
for i in lines_2_delete:
    filt_2_delete = filt_2_delete | df2['Source'].str.contains(i)
filt_CP = df2['Source'].str.contains(":")             #delete devices don't contain :, which are pneumatic connections

lines_2_keep = conf[2].lstrip('lines to keep:').rstrip('\n').split(",")

filt_2_keep = False
for i in lines_2_keep:
    filt_2_keep = filt_2_keep | df2['Source'].str.contains(i)

df_t = df2.loc[(~filt_2_delete) & filt_CP]        #labels don't contain +EXT or +PNM, exclude pneumatic connections
df_tt = df2.loc[filt_2_delete & filt_2_keep & filt_CP]         #labels contain +EXT or +PNM, but also contain -CV or -TT

df2 = pd.concat([df_t, df_tt])

with open("log", 'a', encoding='utf8') as f:
    f.write(datetime.now().strftime("%D   %H:%M:%S") + "\tDeleted wire numbers with '+EXT', '+PNM', ':', but keep '-CV' and '-TT'" + "\n")
 

# print(df2.loc[df2['Source'] == "'=1FT1.12.6+CAB2-TA1:OutDC:-''", 'Source'])
#############  5.1 delete all the 3-phase power wire numbers

Rmvpower = conf[3].lstrip('delete power wire numbers:').rstrip('\n')
if Rmvpower == 'Yes':
    filt1 =(df2['Source'].str.contains('-QA') | df2['Source'].str.contains('-TA'))
    filt2 = False

    filt_ends2delete = [':1',':2',':3',':4',':5',':6',
                        ':L1',':L2',':L3',':U1',':V1',':W1',':U2',':V2',':W2',
                        '/T1','/T2','/T3','/L1','/L2','/L3']
    for i in filt_ends2delete:
        filt2 = filt2 | df2['Source'].str.endswith(i)

    filt1 = filt1 & filt2

    df2.drop(df2[filt1].index, inplace=True)

# print(df2.loc[df2['Source'] == "'=1FT1.12.2+CAB2-TA1:2", 'Source'])
#############  5.2 add label group numbers and locations
pitch = int(conf[4].lstrip('pitch:').rstrip('\n').rstrip(' '))

df2['Prefix'] = conf[5].lstrip('prefix:').rstrip('\n')
df2['Suffix'] = conf[6].lstrip('suffix:').rstrip('\n')

# print(df2.loc[df2['Source'].str.contains("=1FT1.12.6+CAB2-TA1:OutDC:-"), 'Source'])


#############  6. divid DataFrame according to lcations
df2.sort_values('Source', inplace = True)

temp4 = df2['Source location'].value_counts()._info_axis.sort_values()
df3 = pd.DataFrame()
for i in temp4:
    df3 = pd.concat([df3,df2.loc[df2['Source location'] == i]])
df3.set_index('index')
df3.reset_index(inplace=True)
df3['index'] = df3.index
df3['divider'] = (1 + (df3['index'].astype(int)- (df3['index'].astype(int)% pitch))/pitch)
df3['divider'] = df3['divider'].astype(int)
# print(df3)
with open((old_file.rstrip('.xls') + ".txt"), 'w', encoding='utf8') as f:
    df3_string = df3[['Prefix', 'divider', 'Suffix', 'Source']].to_string(header = False, index = False).replace(" ","").replace("'=","=").replace("'+","+")#.lstrip("'")
    df3_string = df3_string.replace("<==","<==\t")          #table symble need to be added at the last stage, not earlier
    f.write(df3_string + "\n")         #write to the file

#####   add location code to the divider strip  #####

with open("log", 'a', encoding='utf8') as f:
    f.write(datetime.now().strftime("%D   %H:%M:%S") + "\tWrite new wire numbers into txt. divid by locations" + "\n\n")

print("Over!, time:",datetime.now().strftime("%H:%M:%S"))
