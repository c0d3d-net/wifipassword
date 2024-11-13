from datetime import datetime, timedelta
from string import ascii_letters, digits
from threading import Thread, Event
from os import system, path, getpid
from psutil import Process
from random import choice
from time import sleep

nstg = 0
running = False
gen_flag = Event()

# Thread 1

start_time = datetime.now()
file = ""

def save_and_exit(generated_strings_list):
    global file
    output_file = file
    print(f"\n\nDie Generierung ist abgeschlossen. Alle Zeilen werden in der Datei {output_file}.")
    with open(output_file, "a") as f:
        f.write("\n".join(generated_strings_list) + "\n")
    print(f"Alle Zeilen werden in einer Datei gespeichert {output_file}.")
    system(f"title Generierung der Zeilen in der Datei ist abgeschlossen {output_file}")

def generate_random_string(length):
    characters = ascii_letters + digits + "#?&!" + ascii_letters + digits + "#?&!"
    return ''.join(choice(characters) for _ in range(length))

def generate_unique_strings(num_strings): 
    global start_time
    seen_strings = set()
    generated_strings = 0
    generated_strings_list = []

    try:
        while generated_strings < num_strings:
            new_string = generate_random_string(8)
            if gen_flag.is_set():
                print("\n\nNotabschaltung. Speichern von Daten...") 
                break
            if new_string not in seen_strings:
                seen_strings.add(new_string)
                generated_strings += 1
                elapsed_time = datetime.now() - start_time
                time_per_string = elapsed_time.total_seconds() / generated_strings
                eta = (num_strings - generated_strings) * time_per_string
                eta_formatted = str(timedelta(seconds=int(eta)))
                speed = generated_strings / elapsed_time.total_seconds()
                elapsed_formatted = str(elapsed_time).split('.')[0]
                progress = f"Erzeugt: {generated_strings}/{num_strings} Zeilen (ETA: {eta_formatted}, Zeit: {elapsed_formatted}, Erzeugungsrate: {speed:.2f} Zeilen/Sek.)             "
                print("\r" + progress, end="")
                generated_strings_list.append(new_string) 
    except Exception as e:
        print(f"Fehler: \n\n{str(e)}\n\n")
        print("\n\nBeendigung im Notfall. Speichern von Daten...")
        save_and_exit(generated_strings_list)
    return generated_strings_list

def main():
    global running, nstg, file
    file = input("Geben Sie einen Dateinamen ein (Bitte ggf. zuvor eine leere Datei mit dem Namen anlegen): ")
    if path.exists(file):
        num_strings_to_generate = int(input("Geben Sie die Anzahl der zu erzeugenden Zeilen ein: "))
        nstg = num_strings_to_generate
    else:
        print("Die Datei existiert nicht..")
        main()

    print("\nBeginn der Erzeugung...\n")
    running = True
    generated_strings_list = generate_unique_strings(num_strings_to_generate)

    save_and_exit(generated_strings_list)
    running = False
    input("Drücken Sie ENTER, um das Programm zu beenden..\n")

# Thread 2

def Title_update():
    global running, nstg
    while not running:
        sleep(1)
    while running and not gen_flag.is_set():
        current_process = Process(getpid())
        ram = (current_process.memory_info().rss // 1024 // 1024) - 3
        cpu = current_process.cpu_percent(interval=0.5)
        system(f"title Erzeugen von {nstg} Zeilen. Verwendet RAM: {ram} MB, CPU Vebrauch: {cpu}")
        sleep(1)

if __name__ == "__main__":
    system("mode con: cols=150 lines=30")
    second_thread = Thread(target=Title_update)
    first_thread = Thread(target=main)

    second_thread.start()
    first_thread.start()

    try:
        while True:
            if not first_thread.is_alive() and not second_thread.is_alive():
                break
            sleep(0.1)
    except KeyboardInterrupt:
        print("\nTastaturunterbrechung erkannt. Anhalten von Streams...")
        gen_flag.set()

    first_thread.join()
    second_thread.join()
