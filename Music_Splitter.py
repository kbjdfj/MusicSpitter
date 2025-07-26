import tkinter as tk
from tkinter import filedialog
from tkinter import ttk

import subprocess
import os

ffmpeg_ok = False
cue_path = []
music_path = []
output_folder = []

ffmpeg_path = []
file_duration = []

input_format = ''
output_format = ['源格式','flac','wav','mp3']
music_profile = {}
music_info = []
def Parse_Cue_File():
    global music_profile
    global music_info
    with open(cue_path[0], 'r') as file:
        lines=file.readlines()
        idx_for_track = 0 
        for idx in range(0, len(lines)):
            #获取专辑名
            if "TITLE" in lines[idx]:
                str_temp = ((lines[idx].replace('\n','')).replace(' ','')).replace('"','')
                music_profile['rem_album'] = str_temp[5:]
            #获取艺术家
            if "PERFORMER" in lines[idx]:
                str_temp = ((lines[idx].replace('\n','')).replace(' ','')).replace('"','')
                music_profile['rem_artist'] = str_temp[9:]
            #获取流派
            if "REM GENRE" in lines[idx]:
                str_temp = ((lines[idx].replace('\n','')).replace(' ','')).replace('"','')
                music_profile['rem_genre'] = str_temp[8:]
            # 获取年份
            if "REM DATE" in lines[idx]:
                str_temp = ((lines[idx].replace('\n','')).replace(' ','')).replace('"','')
                music_profile['rem_date'] = str_temp[7:]
            if 'TRACK' in lines[idx]:
                idx_for_track = idx
                break
        print('idx_for_track = {0}'.format(idx_for_track))
        for idx in range(idx_for_track, len(lines)):
            if "TRACK" in lines[idx]:
                temp_list = ['','','','']
                for offset in range(1,6):
                    try:
                        if 'PERFORMER' in str(lines[idx+offset]):
                            str_temp = ((lines[idx+offset].replace('\n','')).replace(' ','')).replace('"','')
                            perfomer = str_temp[9:]
                            temp_list[0] = perfomer
                        if 'TITLE' in str(lines[idx+offset]):
                            temp_list[1] = (((lines[idx+offset].replace(' ','')).replace('\n','')).replace('TITLE','')).replace('"','')
                        if 'INDEX 00' in str(lines[idx+offset]):
                            str_temp = ((lines[idx+offset].replace('\n',''))).replace('"','')
                            str_temp = str_temp.replace(' ','')
                            str_temp = str_temp[7:]
                            str_temp = '00:'+str_temp[:5]
                            temp_list[2] = str_temp
                        if 'NDEX 01' in str(lines[idx+offset]):
                            str_temp = ((lines[idx+offset].replace('\n',''))).replace('"','')
                            str_temp = str_temp.replace(' ','')
                            str_temp = str_temp[7:]
                            str_temp = '00:'+str_temp[:5]
                            temp_list[3] = str_temp
                        if 'TRACK' in str(lines[idx+offset]):
                            for line in temp_list:
                                music_info.append(line)
                            break
                    except:
                        print("index越界")

    print('music_profile {0}'.format(music_profile))
    text_show.insert(tk.END, f'专辑名{music_profile.get('rem_album','未知')}\n艺术家:{music_profile.get("rem_artist",'未知')}\n年份:{music_profile.get("rem_date",'未知')}\n流派:{music_profile.get("rem_genre",'未知')}\n')
    print('music_info:{0}'.format(music_info))
    
def Time_To_Sec(input):
    return int(input[0:2])*3600 + int(input[3:5])*60 + int(input[6:8])
def Check_Time_Stamp():
    global music_info

    for idx in range(0, int(len(music_info)/4)):
        if music_info[4*idx] == '':
            music_info[4*idx] = music_profile['rem_artist']
        if music_info[4*idx+2] == '':
            music_info[4*idx+2] = music_info[4*idx+3]
    for idx in range(0, int(len(music_info)/4)):
        try:
            music_info[4*idx+3] = music_info[4*(idx+1)+2]
            music_info[4*(idx+1)+2] = music_info[4*(idx+1)+3]
        except:
            print('list index out of range')
    music_info[-1] = file_duration[0]

    for idx in range(0, int(len(music_info)/4)):
        text_show.insert(tk.END, '{0}-{1} {2}-{3}\n'.format(music_info[4*idx],music_info[4*idx+1],music_info[4*idx+2],music_info[4*idx+3]))

    print('music_info from {0}:{1}'.format(Check_Time_Stamp.__name__, music_info))


def Format_Cmd_Line(performer,name, start_time, end_time, out_format):
    global input_format
    codec = [' -c copy ',' -acodec pcm_s16le ',' -acodec flac ',' -codec:a libmp3lame '] #源格式,wav,flac,mp3,
    if 'mp3' in out_format:
        temp_out_path = codec[3]+ os.path.join(output_folder[0], performer+'-'+name+'.'+out_format)
    elif 'flac' in out_format:
        temp_out_path = codec[2]+ os.path.join(output_folder[0], performer+'-'+name+'.'+out_format)
    elif 'wav' in out_format:
        temp_out_path = codec[1]+ os.path.join(output_folder[0], performer+'-'+name+'.'+out_format)
    else:
        # if '源格式' in out_format:
        temp_out_path = codec[0]+ os.path.join(output_folder[0], performer+'-'+name+'.'+input_format)

    temp_out_path = temp_out_path.replace('\\','/')
    cmd = ffmpeg_path[0] + ' -i "' + music_path[0] + '" -hide_banner -ss '+ str(start_time) + ' -to ' + str(end_time) + temp_out_path

    print('cmd: {0}'.format(cmd))
    return cmd

def Get_File_Duration():
    global file_duration

    cmd = ffmpeg_path[0].replace('ffmpeg','ffprobe') + ' -i "' + music_path[0] +'"'
    print('cmd: {0}'.format(cmd))

    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
    stdout, stderr = process.communicate()
    stderr = stderr.split('\n')
    for line in stderr:
        if "Duration:" in line:
            file_duration.append(line.replace(' ','')[9:17])
            text_show.insert(tk.END, '输入文件时长: {0}\n'.format(file_duration))
            break
    Check_Time_Stamp()
    
def Get_Input_Format():
    global input_format
    global music_path
    temp = music_path[0][-6:].split('.')
    input_format = temp[1]
    print('input_format:{0}'.format(input_format))
    text_show.insert(tk.END,'输入格式:{0}\n'.format(input_format))
def Check_Ffmpeg_Ready():
    global ffmpeg_path
    global ffmpeg_ok
    path = os.path.abspath(__file__)
    folder_name = os.path.dirname(path)
    for root, dirs, files in os.walk(folder_name, topdown=False):
        for name in files:
            if "ffmpeg.exe" in name:
                ffmpeg_path.append(os.path.join(root, name))
                print('ffmpeg path:{0}'.format(ffmpeg_path))
                break
    ffmpeg_ok = True

def Select_Cue_File():
    global cue_path
    cue_path.clear()
    cue_path.append(filedialog.askopenfilename())
    print('cue_path:{0}'.format(cue_path[0]))
    text_show.insert(tk.END,cue_path[0]+'\n')
    if True == ffmpeg_ok:
        Parse_Cue_File()
    
def Select_Music_File():
    global music_path
    music_path.clear()
    music_path.append(filedialog.askopenfilename())
    print('music_path:{0}'.format(music_path[0]))
    text_show.insert(tk.END, '输入文件:'+ music_path[0]+'\n')
    Get_Input_Format()
    if True == ffmpeg_ok:
        Get_File_Duration()

def Set_Output_Folder():
    global output_folder
    output_folder.clear()
    output_folder.append(filedialog.askdirectory())
    text_show.insert(tk.END,'输出目录:'+output_folder[0]+'\n')
    print(f'output_folder: {output_folder}')

def Spilt_To_Files():
    for idx in range(0, int(len(music_info)/4)):
        try:
            subprocess.run(Format_Cmd_Line(music_info[4*idx], music_info[4*idx+1], Time_To_Sec(music_info[4*idx+2]), Time_To_Sec(music_info[4*idx+3]), com_output_format.get()))
        except:
            print('分割失败')

Check_Ffmpeg_Ready()
app = tk.Tk()
app.title("音乐文件拆分器")
text_show = tk.Text(app, height=20, width=80)
text_show.grid(row=0, column=0)
btn_choose_cue = tk.Button(app, text="选择CUE文件", command=Select_Cue_File)
btn_choose_cue.grid(row=1, column=0)
btn_choose_music = tk.Button(app, text="选择音乐文件", command=Select_Music_File)
btn_choose_music.grid(row=2, column=0)
btn_choose_output_folder = tk.Button(app, text="选择输出路径", command=Set_Output_Folder)
btn_choose_output_folder.grid(row=3, column=0)
lab_output_format = tk.Label(app, text='输出格式：')
lab_output_format.grid(row=3,column=1)
com_output_format = ttk.Combobox(app,values=output_format)
com_output_format.grid(row=3,column=2)
com_output_format.current(0)
btn_start=tk.Button(app, text="开始", command=Spilt_To_Files)
btn_start.grid(row=4, column=0)

app.mainloop()