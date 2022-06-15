import urllib.request
from urllib.request import urlopen
import PIL
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import xmltodict
import io
import time
import os


class Wolfram(object):
    
    def __init__(self,question):

        #***********use your wolfram app id here***********#
        self.appid="demo"#like: self.appid="XXXXXXXXXXXXXXX"
        self.query=question
        self.url=f"http://api.wolframalpha.com/v2/query?appid={self.appid}&input="
        self.image_url_array=[]
        self.img_array=[]
        self.pod_title=[]

    
    def download_image(self,url):

        #to download the image from url
        image_link=urlopen(url,timeout=20)
        raw =io.BytesIO(image_link.read())
        image =PIL.Image.open(raw).convert('RGBA') 
        return image


    def url_encode(self,query):

        #url encodeing the question
        encoded_query=''
        for word in query:
            if word==' ':
                encoded_query=encoded_query+"%20"
            elif word=='/':
                encoded_query=encoded_query+"%5c"
            elif word=='+':
                encoded_query=encoded_query+"%2B"
            elif word=='&':
                encoded_query=encoded_query+"%26"
            elif word=='=':
                encoded_query=encoded_query+"%3D"
            else :
                encoded_query=encoded_query+word
        #print (encoded_query)
        return encoded_query


    def text_to_img(self,text):

        #font for now
        fnt = ImageFont.truetype('arial.ttf', 15)
        background_color=(255,255,255)
        #creating image size of the text
        image = Image.new(mode = "RGB", size = (10*len(text),20), color = background_color)
        draw = ImageDraw.Draw(image)
        # draw text
        draw.text((1,1), text, font=fnt, fill=(0,240,255))
        return image 


    def response_handling(self,xml):

        #handeling the response wolfram sends
        doc = xmltodict.parse(xml)
        if doc["queryresult"]["@success"]=="false" or doc["queryresult"]["@error"]=="true" or doc["queryresult"]["@numpods"]=="1":
            return False
        
        for i in range(0,len(doc["queryresult"]["pod"])):
            #print(doc["queryresult"]["pod"][i]["@title"])
            
            if (int(doc["queryresult"]["pod"][i]["@numsubpods"]) >1):
                continue
            
            self.pod_title.append(doc["queryresult"]["pod"][i]["@title"])
            self.image_url_array.append(doc["queryresult"]["pod"][i]["subpod"]["img"]["@src"])
        return True


    def image_array_setup(self):

        #adding the pod title and img in pod url 
        for i in range(0,len(self.pod_title)):
            self.img_array.append(self.text_to_img(self.pod_title[i]))
            self.img_array.append(self.download_image(self.image_url_array[i]))
        print("Image download complete")  
        return self.image_processing() 


    def merge_image(self,images):

        #making the image
        widths, heights = zip(*(i.size for i in images))
        new_width = max(widths)+50
        new_height = sum(heights)+100
        new_image = Image.new('RGB', (new_width, new_height), color=(255,255,255))
        offset =20
        for image in images:
            x = 10
            new_image.paste(image, (x, offset))
            offset += image.size[1]+10
        return new_image


    def image_processing(self):

        #the image is appended to list and 
        #split image into multiple if too large
        max_height=300
        temp=[]
        res=[]
        current_height=0

        for i in self.img_array:
            current_height=current_height+i.size[1]
            if current_height>=max_height or current_height >280 :
                res.append(self.merge_image(temp))
                current_height=0
                temp=[]
            temp.append(i)
        try:
            res.append(self.merge_image(temp))
        except ValueError:
            pass
        print ("Image processing Successful")   
        return res


    def output(self):

        #output is in [A,B] where A is true/false depend on 
        #sucess of the query and B is a list which contain 
        #all the image the contains the result
        print("Input: "+self.query)
        start=time.time()
        query=self.url_encode(self.query)
        xml=urlopen(self.url+query).read()
        print ("Connection Sucessful")
        result_check=self.response_handling(xml)
        print ("Checking Wolfram response.....")

        if(result_check):
            print("Got result from Wolfram")
            images_list=self.image_array_setup()
            end=time.time()
            print(f"Runtime:{round(end-start,2)} s")
            return (True,images_list)
        else :
            print("Did not get result from Wolfram")
            return(False,"No Result")
            





if __name__=="__main__":

    question = input("\nEnter your Query:") 
    wolfram=Wolfram(question)
    Is_succesfull=wolfram.output()

    if(Is_succesfull[0]):
        result_list=Is_succesfull[1]

        #To show the first image of the result
        #result_list[0].show()

        #To save all the images of the result in a temp folder src/temp
        try: 
            os.mkdir("temp") 
        except OSError as error: 
            pass
        i=0
        for img in result_list:
            i+=1
            img.save(f"temp/result{i}.png")
        print("Check src/temp folder")      
    else:
        pass  
