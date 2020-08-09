import cv2
from datetime import datetime
import pandas
from bokeh.plotting import figure
from bokeh.io import output_file, show
 
first_frame = None
status_list = [None, None]
time_stamp = []
 
video = cv2.VideoCapture(0)
 
while True:
    check, frame= video.read()
    status = 0
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gaussian_frame = cv2.GaussianBlur(gray_frame, (21,21), 0)
 
    if first_frame is None:
        first_frame = gaussian_frame
        continue
 
    delta_frame = cv2.absdiff(first_frame, gaussian_frame)
 
    threshold_delta_frame = cv2.threshold(delta_frame, 30, 255, cv2.THRESH_BINARY)[1]
 
    threshold_delta_frame_smooth = cv2.dilate(threshold_delta_frame, None, iterations=2)
    
    #contour
    (cnts,_) = cv2.findContours(threshold_delta_frame_smooth.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
 
    for cont in cnts:
        if cv2.contourArea(cont) < 10000:
            continue
        status= 1
        (x, y, w, h)=cv2.boundingRect(cont)
        cv2.rectangle(frame, (x,y), (x+w, y+h), (0,255,0), 3)
 
    cv2.imshow("threshold_delta_frame_smooth", threshold_delta_frame_smooth)
    cv2.imshow("main_frame", frame)
    key = cv2.waitKey(1)
    status_list.append(status)
    
    if status_list[-1]==1 and status_list[-2]==0:
        time_stamp.append(datetime.now())
    if status_list[-1]==0 and status_list[-2]==1:
        time_stamp.append(datetime.now())
    if key == ord('q'):
        if status == 1:
            time_stamp.append(datetime.now())   
        break
print(time_stamp) 
df = pandas.DataFrame(columns=['start', 'end'])
for i in range( 0, len(time_stamp), 2):
    df=df.append({'start': time_stamp[i], 'end': time_stamp[i+1]} , ignore_index=True)
 
df.to_csv('time_stamp.csv')   
 
video.release()
cv2.destroyAllWindows()
d1= pandas.read_csv("time_stamp.csv", parse_dates = ['start', 'end'] )
 
output_file("motions.html")
 
p = figure(width=300, height=300, x_axis_type = "datetime")
p.quad(top=10, bottom=0, left=d1["start"], right=d1["end"], color="green")
 
show(p)