from environs import Env

# Теперь используем вместо библиотеки python-dotenv библиотеку environs
env = Env()
env.read_env()

BOT_TOKEN = env.str("BOT_TOKEN")  # Забираем значение типа str
ADMINS = env.list("ADMINS", subcast=int)  # Тут у нас будет список из админов
IP = env.str("ip")  # Тоже str, но для айпи адреса хоста
PGUSER = env.str("PGUSER")
PGPASSWORD = env.str("PGPASS")
DATABASE = env.str("DATABASE")
db_host = IP

ITAD_API_KEY = env.str("ITAD_API_KEY")

POSTGRES_URI = f"postgresql://{PGUSER}:{PGPASSWORD}@{db_host}/{DATABASE}"
