from student import Database,Main,check_and_create_tables,create_tables


if __name__=="__main__":
    check_and_create_tables()
    database = Database()
    main = Main()
    main.run()
    
    

    