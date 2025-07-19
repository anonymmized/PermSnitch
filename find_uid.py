import subprocess 

ids = subprocess.check_output(['id'])
ids = ids.decode('utf-8')[4:].replace(',', ' ').split()
cur_ids = {}
for id in ids:
    if '=' in id:
        splited_id = id.replace('(', ' ').split()
        first_part = splited_id[0]
        second_part = splited_id[1][:-1]
        cur_ids[first_part] = second_part
    else:
        splited_id = id.replace('(', ' ').split()
        first_part = splited_id[0]
        second_part = splited_id[1][:-1]
        cur_ids[first_part] = second_part
    

uid = '501'
for key, value in cur_ids.items():
    if key == uid:
        print(value)