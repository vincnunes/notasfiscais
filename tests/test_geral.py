def main():
    nota = "23044002223674714000180000000000007326110762388170"
    print("ESTADO: ", nota[:2])
    print("CIDADE:", nota[:7])
    print("DESCONHECIDO: ", nota[7:9])
    print("CNPJ: ", nota[9:23])
    print("NOTA: ", nota[23:36])
    print("CODIGO: ", nota[36:40])
    print("ID: ", nota[40:50])
    print("NUMERO DA NOTA: ", int(nota[23:36]))

if __name__ == "__main__":
    main()