import urllib.request
from urllib.request import urlopen
import PIL
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import xmltodict
import io
import time



class Wolfram(object):


    def __init__(self,question):

        self.appid="########use your wolfram app id here########"
        self.query=question
        self.url=f"http://api.wolframalpha.com/v2/query?appid={self.appid}&input="
        self.image_url_array=[]
        self.img_array=[]
        self.pod_title=[]

    
    def download_image(self,url):

        #to download the image from url
        imag=urlopen(url)
        raw = io.BytesIO(imag.read())
        return PIL.Image.open(raw).convert('RGBA')


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
        print (encoded_query)
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
              
        print("feching image_url and title compleate")
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
        new_im = Image.new('RGB', (new_width, new_height), color=(255,255,255))

        offset =20
        for im in images:
            x = 10
        
            new_im.paste(im, (x, offset))
            offset += im.size[1]+10
        return new_im



    def image_processing(self):

        #the image is appended to list and 
        #split image into multiple if too large
        max_height=300
        temp=[]
        re=[]
        current_height=0

        for i in self.img_array:
            current_height=current_height+i.size[1]

            if current_height>=max_height or current_height >280 :
                re.append(self.merge_image(temp))
                current_height=0
                temp=[]
            temp.append(i)
        try:
            re.append(self.merge_image(temp))
        except ValueError:
            pass
        print ("Image processing Successfull")   
        return re

    def output(self):

        #output is in [A,B] where A is true/false depend on 
        #sucess of the query and B is a list which contain 
        #all the image the contains the result
        start=time.time()
        query=self.url_encode(self.query)
        xml=urlopen(self.url+query).read()
        print ("success connecting")
        result_check=self.response_handling(xml)
        print ("Checking Wolfram response")
        if(result_check):
            a=self.image_array_setup()
            end=time.time()
            print(f"Runtime:{end-start}")
            return (True,a)
        else :
            return(False,"a")
            





if __name__=="__main__":
    #test to show the first image of the result
    a=Wolfram("2+2")
    a.output()[1][0].show()
    print("done")


