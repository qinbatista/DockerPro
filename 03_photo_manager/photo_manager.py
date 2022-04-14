#%%
print("start...")
from datetime import datetime
import os
import time
import shutil
def get_time():
	current_time = datetime.now().strftime("%Y-%m")
	current_folder = "./"+current_time
	if not os.path.exists(current_folder):os.makedirs(current_folder)
	return current_time, current_folder

# %%
def analysis_folder():
	'''
	return first param is folder_list, second is file_list
	'''
	file_name_lists = os.listdir('.')
	folder_list =[]
	file_list = []
	for file_name_list in file_name_lists:
		if file_name_list.find(".")!=-1 and file_name_list.find(".")!=0 and file_name_list.find(os.path.basename(__file__))==-1:
			file_list.append(file_name_list)
		else:
			folder_list.append(file_name_list)
	return folder_list,file_list
# %%
def loop_command():
	print(os.listdir('.'))
	print("negivate...")
	os.chdir('/photo_manager')
	print(os.listdir('.'))
	while True:
		current_time,current_folder = get_time()
		folder_list,file_list = analysis_folder()
		for file_name in file_list:
			print("file_name:"+file_name)
			print("current_folder/file_name:"+current_folder+"/"+file_name)
			shutil.move(file_name, current_folder+"/"+file_name)
		time.sleep(5)
if __name__ == "__main__":
	loop_command()
# %%
