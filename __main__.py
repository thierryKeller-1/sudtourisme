from dotenv import load_dotenv
from utils import check_arguments, main_arguments, SUDTOURISME_FIELDS
from toolkits import file_manager as fm
# from edomizil.scraper import EdomizilScraper
from initializer import run_initialization, setup_scraping
from scraper import run_scraping
from utils import SUDTOURISME_FIELDS
import os





if __name__=='__main__':

    load_dotenv()

    args = main_arguments()

    if args.action:
        match args.action:
            case 'start':
                miss_args = check_arguments(args, ['-n', '-d', '-w'])
                if not len(miss_args):
                    metadata = {}
                    metadata["week_scrap"] = args.weekscrap
                    metadata["config_name"] = args.name
                    print('info', "scraping...")
                    data = []
                    base_log:dict = metadata
                    base_log["last_index"] = 0
                    base_log["finished"] = False
                    base_output:list = []

                    log_folder_path:str = f"{os.environ.get('LOG_FOLDER_PATH')}/{metadata.get('week_scrap').replace('/',  '_')}/"
                    output_folder_path:str = f"{os.environ.get('OUTPUT_FOLDER_PATH')}/{metadata.get('week_scrap').replace('/',  '_')}/"
                    dest_folder_path:str = f"{os.environ.get('DESTS_FOLDER_PATH')}/scraps/{metadata.get('week_scrap').replace('/',  '_')}/"

                    fm.create_folder_if_not_exist(log_folder_path)
                    fm.create_folder_if_not_exist(output_folder_path)

                    metadata["log_file"] = f"{log_folder_path}{metadata.get('config_name')}.json" 
                    metadata["ouput_file"] = f"{output_folder_path}{metadata.get('config_name')}.csv" 
                    metadata["dest_file"] = f"{dest_folder_path}{metadata.get('config_name')}.json"

                    if not fm.is_file_exist(metadata.get("log_file")):
                        fm.create_or_update_json_file(metadata.get('log_file'), base_log)

                    if not fm.is_file_exist(metadata.get("ouput_file")):
                        fm.create_csv_file(metadata.get('output_file'), SUDTOURISME_FIELDS)

                    logs = fm.get_json_file_content(metadata.get("log_file"))
                    print('info',f"logs {logs}")

                    index = logs.get("last_index", 0)

                    destinations = fm.get_json_file_content(metadata.get("dest_file"))

                    print(len(destinations))

                    while index <= len(destinations):
                        index = logs.get("last_index", 0)
                        curent_dest = destinations[index]
                        metadata["current_dest"] = curent_dest 
                        run_scraping(metadata)
                        logs["last_index"] = index + 1
                        fm.create_or_update_json_file(metadata.get('log_file'), logs)
                        
                else:
                    raise Exception(f"Argument(s) manquant(s): {', '.join(miss_args)}") 

            case 'init':
                miss_args = check_arguments(args, ['-n', '-w', '-b', '-e', '-f'])
                if not len(miss_args):
                    metadata = {}
                    metadata["week_scrap"] = args.weekscrap
                    metadata["dest_name"] = args.name
                    metadata["start_date"] = args.start_date
                    metadata["end_date"] = args.end_date
                    metadata["frequency"] = args.frequency
                    # run_initialization(metadata)
                    setup_scraping(metadata)
                else:
                    raise Exception(f"Argument(s) manquant(s): {', '.join(miss_args)}") 
                
    else:
        print('   => action argument should be defined in order to launch scrap')