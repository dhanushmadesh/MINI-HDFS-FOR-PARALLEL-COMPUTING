import os
import multiprocessing
from collections import Counter
import re
from colorama import Fore, Style, init
from MINI_HDFS import split_and_store, list_files, get_chunk_paths

# init colors
init(autoreset=True)


def show_header(title):
    print(f"\n{Fore.CYAN}{'=' * 70}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}{title.center(70)}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'=' * 70}{Style.RESET_ALL}\n")


def show_menu():
    show_header("MINI HDFS - PARALLEL COMPUTING")
    print(f"{Fore.MAGENTA}1. Upload & Split File")
    print(f"{Fore.MAGENTA}2. View Metadata")
    print(f"{Fore.MAGENTA}3. Run Parallel Analysis")
    print(f"{Fore.MAGENTA}4. Exit")
    return input(f"\n{Fore.CYAN}Enter choice: {Style.RESET_ALL}").strip()


def show_job_menu():
    show_header("Select Analysis Job")
    print(f"{Fore.MAGENTA}1. Word Count")
    print(f"{Fore.MAGENTA}2. Most Frequent Word")
    return input(f"\n{Fore.CYAN}Enter job type (1-2): {Style.RESET_ALL}").strip()


# MAP FUNCTIONS
def map_word_count(text):
    """Returns a counter for word count only."""
    words = text.split()
    return Counter({"word_count": len(words)})


def map_top_word(text):
    """Returns full counter of ALL words for global frequency."""
    words = re.findall(r"\b[a-zA-Z0-9']+\b", text.lower())
    return Counter(words)


# REDUCE FUNCTION
def reduce_results(list_of_counters):
    combined = Counter()
    for c in list_of_counters:
        combined.update(c)
    return combined


# WORKER
def process_chunk(args):
    path, job = args
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    if job == "word_count":
        return map_word_count(text)
    return map_top_word(text)


def run_parallel_analysis(file_name, job_type):
    chunk_paths = get_chunk_paths(file_name)
    if not chunk_paths:    #file not found 
        print(Fore.RED + "ERROR: No chunks found." + Style.RESET_ALL)
        return

    print(Fore.CYAN + f"\nRunning '{job_type}' on {len(chunk_paths)} chunks...\n" + Style.RESET_ALL)

    # Parallel processing
    with multiprocessing.Pool() as pool:
        results = pool.map(process_chunk, [(p, job_type) for p in chunk_paths])

    # Reduce phase
    final = reduce_results(results)

    print(Fore.GREEN + "Final Result:" + Style.RESET_ALL)

    # WORD COUNT
    if job_type == "word_count":
        total_words = final["word_count"]
        print(f"{Fore.YELLOW}Total Words: {total_words}{Style.RESET_ALL}")

    # MOST FREQUENT WORD (GLOBAL)
    else:
        # If word_count key is present, remove it
        if "word_count" in final:
            del final["word_count"]

        # Get actual global most frequent word
        most_common_word, count = final.most_common(1)[0]
        print(f"{Fore.YELLOW}Most Frequent Word: '{most_common_word}' ({count} times){Style.RESET_ALL}")

    print("\n" + Fore.CYAN + "=" * 70 + Style.RESET_ALL + "\n")



def main():
    while True:
        choice = show_menu()

        if choice == "1":
            file_path = input(Fore.WHITE + "Enter path to file: " + Style.RESET_ALL).strip()
            if os.path.exists(file_path):
                split_and_store(file_path)
            else:
                print(Fore.RED + "ERROR: File not found." + Style.RESET_ALL)

        elif choice == "2":
            list_files()

        elif choice == "3":
            list_files()
            file_name = input(Fore.WHITE + "Enter exact file name: " + Style.RESET_ALL).strip()

            job_choice = show_job_menu()
            job_map = {"1": "word_count", "2": "top_word"}
            job_type = job_map.get(job_choice, "word_count")

            run_parallel_analysis(file_name, job_type)

        elif choice == "4":
            print(Fore.YELLOW + "\nExiting program.\n" + Style.RESET_ALL)
            break

        else:
            print(Fore.RED + "ERROR: Invalid choice." + Style.RESET_ALL)


if __name__ == "__main__":
    main()

