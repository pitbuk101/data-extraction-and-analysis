#importing required libraries
import pandas as pd
import requests
from bs4 import BeautifulSoup
import numpy as np

import re

#importing nltk library and stopwords
import nltk
import string



#importing tokenize library
from nltk.tokenize import word_tokenize

import nltk
nltk.download('punkt')



import warnings
warnings.filterwarnings("ignore")

#importing input file
df=pd.read_excel(r'C:\Users\tprat\Downloads\DATA_PREP-20230228T164907Z-001\DATA_PREP\Input.xlsx')[['URL_ID','URL']]



#importing stop words files that are provided

StopWords_Auditor=pd.read_csv(r"C:\Users\tprat\Downloads\DATA_PREP-20230228T164907Z-001\DATA_PREP\StopWords\StopWords_Auditor.txt",header=None)
with open(r"C:\Users\tprat\Downloads\DATA_PREP-20230228T164907Z-001\DATA_PREP\StopWords\StopWords_Currencies.txt") as f:
    data = [list(map(str, row.split())) for row in f.read().split('\n\n')]

StopWords_Currencies = pd.DataFrame(data)
StopWords_Currencies = StopWords_Currencies.transpose()
StopWords_DatesandNumbers=pd.read_csv(r"C:\Users\tprat\Downloads\DATA_PREP-20230228T164907Z-001\DATA_PREP\StopWords\StopWords_DatesandNumbers.txt",header=None)
StopWords_Generic=pd.read_csv(r"C:\Users\tprat\Downloads\DATA_PREP-20230228T164907Z-001\DATA_PREP\StopWords\StopWords_Generic.txt",header=None)
StopWords_GenericLong=pd.read_csv(r"C:\Users\tprat\Downloads\DATA_PREP-20230228T164907Z-001\DATA_PREP\StopWords\StopWords_GenericLong.txt",header=None)
StopWords_Geographic=pd.read_csv(r"C:\Users\tprat\Downloads\DATA_PREP-20230228T164907Z-001\DATA_PREP\StopWords\StopWords_Geographic.txt",header=None)
StopWords_Names=pd.read_csv(r"C:\Users\tprat\Downloads\DATA_PREP-20230228T164907Z-001\DATA_PREP\StopWords\StopWords_Names.txt",header=None)



#importing master Dictionary

positive=pd.read_csv(r"C:\Users\tprat\Downloads\DATA_PREP-20230228T164907Z-001\DATA_PREP\MasterDictionary\positive-words.txt",header=None)
with open(r"C:\Users\tprat\Downloads\DATA_PREP-20230228T164907Z-001\DATA_PREP\MasterDictionary\negative-words.txt") as f:
    data_neg = [list(map(str, row.split())) for row in f.read().split('\n\n')]
negative = pd.DataFrame(data_neg)
negative = negative.transpose()



df=df.iloc[0:114]
print(df)

orignal_df = df.copy()

df.drop('URL_ID',axis=1,inplace=True)





#################    Data Extraction     #######################

#extracting text from all the url
url_id=1
df_data = pd.Series()
no_content_index = []
for i in range(0,len(df)):
  
    j=df.iloc[i].values
    #print(i)
    
    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'}#giving user access
    page=requests.get(j[0],headers=headers)     
    soup=BeautifulSoup(page.content,'html.parser')                #parsing url text
    content=soup.findAll(attrs={'class':'td-post-content'})                #extracting only text part
    if content:
      content=content[0].text.replace('\xa0',"  ").replace('\n',"  ")      #replace end line symbol with space
    else:
        no_content_index.append(i)
        print(f"We find No Content at link {j} which is at index {i}")
        continue 
    title=soup.findAll(attrs={'class':'entry-title'})                           #extracting title of website
    title=title[16].text.replace('\n',"  ").replace('/',"")
    text=title+ '.' +content                                                    #merging title and content text
    text=np.array(text)                                                         #converting to array form
    text.reshape(1,-1)                                                          #changing shape to 1d 
    df1 = pd.Series(text)                                                       #creating series data frame
   #  print(df1)
    

    df_data = df_data.append(df1).reset_index(drop=True)                        # getting all data

    url_id+=1

## droping no content/text link that found
print(no_content_index)                                                         #drop no content
orignal_df.drop(no_content_index, inplace = True)
print(f'no content {orignal_df}')

print("extracted data")
print(df_data)







                        ############     Data Analysis    ###########


# extracted files

df_all = df_data.copy()  
df_all = df_all.to_frame()
print(df_all.info())


output=pd.DataFrame()
#output.columns=['POSITIVE SCORE','NEGATIVE SCORE','POLARITY SCORE','SUBJECTIVITY SCORE','AVG SENTENCE LENGTH','PERCENTAGE OF COMPLEX WORDS','FOG INDEX','AVG NUMBER OF WORDS PER SENTENCE','COMPLEX WORD COUNT','WORD COUNT','SYLLABLE PER WORD','PERSONAL PRONOUNS','AVG WORD LENGTH']

for row in df_all.iterrows():
    print(row)
    element = row[1]
    element = element.astype(str)
    a=element.str.split('([\.]\s)',expand=False)                               #splitting text on '.'
    b=a.explode()                                                              #converting to rows
    b=pd.DataFrame(b)                                                          #creating data frame
    b.columns=['abc']
    # print(b)
    
    #removing . char from each rows
    def abcd(x):    
        nopunc =[char for char in x if char != '.']
        return ''.join(nopunc)
    b['abc']=b['abc'].apply(abcd)
    
    #print(b)
    
    #replacing empty space with null values
    
    c=b.replace('',np.nan,regex=True)
    c=c.mask(c==" ")
    c=c.dropna()
    c.reset_index(drop=True,inplace=True)
    # print(c)
    
    punc=[punc for punc in string.punctuation]
    print(punc)
    
    
    #creating func for removing stop words
    
    
    def text_process(text):
        nopunc =[char for char in text if char not in punc or char not in [':',',','(',')','’','?']]
        nopunc=''.join(nopunc)
        txt=' '.join([word for word in nopunc.split() if word.lower() not in StopWords_Auditor])
        txt1=' '.join([word for word in txt.split() if word.lower() not in StopWords_Currencies])
        txt2=' '.join([word for word in txt1.split() if word.lower() not in StopWords_DatesandNumbers])
        txt3=' '.join([word for word in txt2.split() if word.lower() not in StopWords_Generic])
        txt4=' '.join([word for word in txt3.split() if word.lower() not in StopWords_GenericLong])
        txt5=' '.join([word for word in txt4.split() if word.lower() not in StopWords_Geographic])
        return ' '.join([word for word in txt5.split() if word.lower() not in StopWords_Names])
    
    #applying func for each row
    c['abc']=c['abc'].apply(text_process)
    print(c)
    
    
    print(f"positive dataframe \n {positive}")
    print(f"positive dataframe \n {negative}")
    positive.columns=['abc']
    negative.columns=['abc']
    positive['abc']=positive['abc'].astype(str)
    negative['abc']=negative['abc'].astype(str)
    
    #positive and negative dictionary without stopwords
    positive['abc']=positive['abc'].apply(text_process)
    negative['abc']=negative['abc'].apply(text_process)
    
    
    #positive list
    length=positive.shape[0]
    post=[]
    for i in range(0,length):
        nopunc =[char for char in positive.iloc[i] if char not in string.punctuation or char != '+']
        nopunc=''.join(nopunc)
        post.append(nopunc)
                     
        

    #negative list
    length=negative.shape[0]
    neg=[]
    for i in range(0,length):
        nopunc =[char for char in negative.iloc[i] if char not in string.punctuation or char != '+']
        nopunc=''.join(nopunc)
        neg.append(nopunc)
        
    
    #tokenize
    
    txt_list=[]
    length=c.shape[0]
    for i in range(0,length):
        txt=' '.join([word for word in c.iloc[i]])
        txt_list.append(txt)
        
    #tokenization of text
    tokenize_text=[]
    for i in txt_list:
        tokenize_text+=(word_tokenize(i))
    
    print(tokenize_text)
    print(len(tokenize_text))
    
    
    
    
    ### POSITIVE SCORE
    
    positive_score=0
    for i in tokenize_text:     
        if(i.lower() in post):
            positive_score+=1
    print('postive score=', positive_score)
    
    
    ### NEGATIVE SCORE
    
    negative_score=0
    for i in tokenize_text:
        if(i.lower() in neg):
            negative_score+=1
    print('negative score=', negative_score)
    
    
    ### POLARITY SCORE 
    
    #Polarity Score = (Positive Score – Negative Score)/ ((Positive Score + Negative Score) + 0.000001)
    Polarity_Score=(positive_score-negative_score)/((positive_score+negative_score)+0.000001)
    print('polarity_score=', Polarity_Score)
    
    
    ### SUBJECTIVITY SCORE

    #Subjectivity Score = (Positive Score + Negative Score)/ ((Total Words after cleaning) + 0.000001)
    subjectiivity_score=(positive_score-negative_score)/((len(tokenize_text))+ 0.000001)
    print('subjectivity_score',subjectiivity_score)
    
    
    ### AVG SENTENCE LENGTH
    
    length=c.shape[0]
    avg_length=[]
    for i in range(0,length):
        avg_length.append(len(c['abc'].iloc[i]))
    avg_senetence_length=sum(avg_length)/len(avg_length)
    print('avg sentence length=', avg_senetence_length)


    ### PERCENTAGE OF COMPLEX WORDS
    
    vowels=['a','e','i','o','u']
    count=0
    complex_Word_Count=0
    for i in tokenize_text:
        x=re.compile('[es|ed]$')
        if x.match(i.lower()):
            count+=0
        else:
            for j in i:
                if(j.lower() in vowels ):
                    count+=1
        if(count>2):
            complex_Word_Count+=1
        count=0

    Percentage_of_Complex_words=complex_Word_Count/len(tokenize_text)
    print('percentag of complex words= ',Percentage_of_Complex_words)
    
    
    ### FOG INDEX
    
    #Fog Index = 0.4 * (Average Sentence Length + Percentage of Complex words)
    Fog_Index = 0.4 * (avg_senetence_length + Percentage_of_Complex_words)
    print('fog index= ',Fog_Index )
    
    
    
    ### AVG NUMBER OF WORDS PER SENTENCE
    length=c.shape[0]
    avg_length=[]
    for i in range(0,length):
          a=[word.split( ) for word in c.iloc[i]]
          avg_length.append(len(a[0]))
          a=0
    avg_no_of_words_per_sentence=sum(avg_length)/length
    print("avg no of words per sentence= ",avg_no_of_words_per_sentence)
  
    
    
    ### COMPLEX WORD COUNT
    
    vowels=['a','e','i','o','u']
    count=0
    complex_Word_Count=0
    for i in tokenize_text:
        x=re.compile('[es|ed]$')
        if x.match(i.lower()):
          count+=0
        else:
          for j in i:
            if(j.lower() in vowels ):
              count+=1
        if(count>2):
          complex_Word_Count+=1
        count=0

    print('complex words count=',  complex_Word_Count)
        
    
    
    ### WORD COUNT
    
    word_count=len(tokenize_text)
    print('word count= ', word_count)
    
    
    
    ###  SYLLABLE PER WORD
    
    vowels=['a','e','i','o','u']
    count=0
    for i in tokenize_text:
        x=re.compile('[es|ed]$')
        if x.match(i.lower()):
          count+=0
        else:
          for j in i:
            if(j.lower() in vowels ):
              count+=1
    syllable_count=count
    print('syllable_per_word= ',syllable_count)
    
    
    
    ### PERSONAL PRONOUNS
    
    pronouns=['i','we','my','ours','us' ]
    count=0
    for i in tokenize_text:
        if i.lower() in pronouns:
          count+=1
    personal_pronouns=count
    print('personal pronouns= ',personal_pronouns )
    
    
    ### AVG WORD LENGTH
    
    count=0
    for i in tokenize_text:
      for j in i:
        count+=1
    avg_word_length=count/len(tokenize_text)
    print('avg word= ', avg_word_length)
    
    
    data={'POSITIVE SCORE':positive_score,'NEGATIVE SCORE':negative_score,'POLARITY SCORE':Polarity_Score,'SUBJECTIVITY SCORE':subjectiivity_score,'AVG SENTENCE LENGTH':avg_senetence_length,'PERCENTAGE OF COMPLEX WORDS':Percentage_of_Complex_words,'FOG INDEX':Fog_Index,'AVG NUMBER OF WORDS PER SENTENCE':avg_no_of_words_per_sentence,'COMPLEX WORD COUNT':complex_Word_Count,'WORD COUNT':word_count,'SYLLABLE PER WORD':syllable_count,'PERSONAL PRONOUNS':personal_pronouns,'AVG WORD LENGTH':avg_word_length}

    output=output.append(data,ignore_index=True)


## Reset index and merge for output structure

orignal_df.reset_index(drop=True, inplace=True)
output.reset_index(drop=True, inplace=True)
df_final_output = pd.concat([orignal_df, output], axis=1)
print(df_final_output)
print(df_final_output.shape)

df_final_output.to_csv('final_output.csv', index=False)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    