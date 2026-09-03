import kurtz_1, palacio

def jugar_de_nuevo(resp: str):
    if resp.upper() == "Y":
        return True
    elif resp.upper() == "N":
        return False
    else:
        return True

def main():
    while True:
        resp = input(f"""
- Desea jugar según la primera parte del proyecto (1)
- Desea jugar según la segnda parte del proyecto (2)
- Salir (3)
                    
Modo: """)
        
        if resp == "1":
            kurtz_1.main()
            jugar_otra_vez = input("Quieres jugar de nuevo (Y/N) ")
            if not jugar_de_nuevo(jugar_otra_vez):
                print("Hasta la próxima")
                break

        elif resp == "2":
            palacio.main()
            jugar_otra_vez = input("Quieres jugar de nuevo (Y/N) ")
            if not jugar_de_nuevo(jugar_otra_vez):
                print("Hasta la próxima")
                break
        
        elif resp == "3":
            print("Hasta la próxima")
            break
        
        else:
            print("UPS! No he entendido eso")
            resp = input(f"""
- Desea jugar según la primera parte del proyecto (1)
- Desea jugar según la segnda parte del proyecto (2)
- Salir (3)
                    
Modo: """)

if __name__=="__main__":

    main()