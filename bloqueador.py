# Importa o módulo 'os' para interagir com o sistema operacional
import os
# Importa o módulo 'tkinter' para criar a interface gráfica
import tkinter as tk
# Importa 'messagebox' e 'simpledialog' do tkinter para caixas de diálogo
from tkinter import messagebox, simpledialog
# Importa 'json' para manipular arquivos JSON
import json
# Importa 're' para trabalhar com expressões regulares
import re
# Importa 'shutil' para operações de arquivo como cópia
import shutil

# Define o caminho do arquivo 'hosts' dependendo do sistema operacional (Windows ou Linux/Mac)
hosts_path = r"C:\Windows\System32\drivers\etc\hosts" if os.name == "nt" else "/etc/hosts"
# Define o caminho para o backup do arquivo hosts
hosts_backup = hosts_path + ".bak"
# Nome do arquivo JSON que armazenará a lista de sites bloqueados
blocked_sites_file = "blocked_sites.json"
# IP para redirecionamento (localhost)
redirect = "127.0.0.1"
# Lista vazia que armazenará os sites bloqueados
blocked_sites = []

# Função para salvar a lista de sites bloqueados em um arquivo JSON
def save_blocked_sites():
    with open(blocked_sites_file, "w") as file:
        json.dump(blocked_sites, file)

# Função para carregar a lista de sites bloqueados do arquivo JSON
def load_blocked_sites():
    global blocked_sites  # Permite modificar a variável global 'blocked_sites'
    try:
        with open(blocked_sites_file, "r") as file:
            blocked_sites = json.load(file)
    except FileNotFoundError:  # Se o arquivo não existir, mantém a lista vazia
        blocked_sites = []

# Função para validar se um site tem um formato válido (ex: www.exemplo.com)
def is_valid_site(site):
    pattern = r"^(www\.)?[\w-]+\.[a-z]{2,}$"  # Expressão regular para validar URLs
    return re.match(pattern, site)  # Retorna True se o site for válido

# Função para criar um backup do arquivo hosts (se não existir)
def backup_hosts():
    if not os.path.exists(hosts_backup):  # Verifica se o backup já existe
        shutil.copy(hosts_path, hosts_backup)  # Cria uma cópia do arquivo hosts

# Função para restaurar o arquivo hosts original a partir do backup
def restore_hosts_backup():
    if os.path.exists(hosts_backup):  # Verifica se o backup existe
        shutil.copy(hosts_backup, hosts_path)  # Restaura o arquivo hosts original

# Função para adicionar um site à lista de bloqueio (interface gráfica)
def add_site_gui():
    # Abre uma caixa de diálogo para o usuário digitar o site
    site = simpledialog.askstring("Adicionar Site", "Digite o site (ex: www.exemplo.com):")
    if site and is_valid_site(site):  # Verifica se o site é válido e não está vazio
        if site not in blocked_sites:  # Verifica se o site já não está na lista
            blocked_sites.append(site)  # Adiciona o site à lista
            update_listbox()  # Atualiza a lista na interface
            save_blocked_sites()  # Salva a lista no arquivo JSON
            messagebox.showinfo("Sucesso", f"Site '{site}' adicionado à lista de bloqueio.")
        else:
            messagebox.showwarning("Aviso", "Site já está na lista!")  # Site duplicado
    else:
        messagebox.showwarning("Aviso", "Site inválido!")  # Site com formato inválido

# Função para remover um site da lista de bloqueio (interface gráfica)
def remove_site_gui():
    try:
        # Obtém o site selecionado na ListBox
        selected = listbox.get(listbox.curselection())
        blocked_sites.remove(selected)  # Remove o site da lista
        update_listbox()  # Atualiza a ListBox
        save_blocked_sites()  # Salva a lista no arquivo JSON
        messagebox.showinfo("Sucesso", f"Site '{selected}' removido da lista.")
    except tk.TclError:  # Se nenhum site estiver selecionado
        messagebox.showwarning("Aviso", "Nenhum site selecionado para remover.")

# Função para ativar o bloqueador (modifica o arquivo hosts)
def activate_blocker_gui():
    # Pede confirmação antes de ativar
    if messagebox.askyesno("Confirmação", "Tem certeza de que deseja ativar o bloqueador?"):
        try:
            backup_hosts()  # Cria um backup do arquivo hosts
            with open(hosts_path, "r+") as file:  # Abre o arquivo hosts para leitura e escrita
                content = file.readlines()  # Lê todas as linhas do arquivo
                file.seek(0)  # Volta ao início do arquivo
                # Reescreve apenas as linhas que não contêm sites bloqueados
                for line in content:
                    if not any(site in line for site in blocked_sites):
                        file.write(line)
                # Adiciona os redirecionamentos para os sites bloqueados
                for site in blocked_sites:
                    file.write(f"{redirect} {site}\n")
                file.truncate()  # Remove conteúdo excedente
            messagebox.showinfo("Sucesso", "Bloqueador ativado.")
        except PermissionError:  # Se não tiver permissão para editar o arquivo
            messagebox.showerror("Erro", "Permissão negada. Execute o programa como administrador.")

# Função para desativar o bloqueador (remove as regras do arquivo hosts)
def deactivate_blocker_gui():
    # Pede confirmação antes de desativar
    if messagebox.askyesno("Confirmação", "Tem certeza de que deseja desativar o bloqueador?"):
        try:
            backup_hosts()  # Cria um backup do arquivo hosts
            with open(hosts_path, "r+") as file:
                content = file.readlines()
                file.seek(0)
                # Reescreve apenas as linhas que não contêm sites bloqueados
                for line in content:
                    if not any(site in line for site in blocked_sites):
                        file.write(line)
                file.truncate()  # Remove conteúdo excedente
            messagebox.showinfo("Sucesso", "Bloqueador desativado.")
        except PermissionError:
            messagebox.showerror("Erro", "Permissão negada. Execute o programa como administrador.")

# Função para restaurar o arquivo hosts original (usando o backup)
def restore_original_gui():
    # Pede confirmação antes de restaurar
    if messagebox.askyesno("Confirmação", "Tem certeza de que deseja restaurar o arquivo 'hosts'?"):
        try:
            restore_hosts_backup()  # Restaura o arquivo hosts original
            messagebox.showinfo("Sucesso", "Arquivo 'hosts' restaurado com sucesso.")
        except Exception as e:  # Captura qualquer erro durante a restauração
            messagebox.showerror("Erro", f"Erro ao restaurar o arquivo: {e}")

# Função para atualizar a ListBox com os sites bloqueados
def update_listbox():
    listbox.delete(0, tk.END)  # Limpa a ListBox
    for site in blocked_sites:  # Adiciona cada site da lista à ListBox
        listbox.insert(tk.END, site)

# Decorador para exibir erros em caixas de diálogo
def show_error_dialog(func):
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)  # Executa a função original
        except Exception as e:  # Captura qualquer erro
            messagebox.showerror("Erro", f"Ocorreu um erro: {e}")  # Exibe o erro
    return wrapper

# Aplica o decorador de tratamento de erros às funções da interface
add_site_gui = show_error_dialog(add_site_gui)
remove_site_gui = show_error_dialog(remove_site_gui)
activate_blocker_gui = show_error_dialog(activate_blocker_gui)
deactivate_blocker_gui = show_error_dialog(deactivate_blocker_gui)

# Configuração da janela principal
root = tk.Tk()
root.title("Bloqueador de Sites")  # Título da janela
root.geometry("400x300")  # Tamanho inicial da janela
root.resizable(True, True)  # Permite redimensionamento
root.configure(bg="pink")  # Cor de fundo da janela

# Label (título do programa)
label = tk.Label(root, text="Bloqueador de Sites", font=("Arial", 12, "bold"), bg="pink", fg="hot pink")
label.pack(pady=5)  # Posiciona o label na janela

# Frame para organizar a ListBox e a barra de rolagem
frame = tk.Frame(root, bg="pink")
frame.pack(pady=5, fill=tk.BOTH, expand=True)  # Expande para ocupar espaço disponível

# ListBox para exibir os sites bloqueados
listbox = tk.Listbox(frame, width=30, height=6, bg="white", fg="hot pink", selectbackground="light pink")
listbox.pack(side=tk.LEFT, padx=5, fill=tk.BOTH, expand=True)  # Posiciona à esquerda

# Barra de rolagem para a ListBox
scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL, command=listbox.yview, bg="pink")
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)  # Posiciona à direita
listbox.config(yscrollcommand=scrollbar.set)  # Vincula a barra de rolagem à ListBox

# Estilo padrão para os botões
btn_style = {"bg": "white", "fg": "hot pink", "activebackground": "light pink", "width": 15}

# Botão para adicionar sites
btn_add = tk.Button(root, text="Adicionar Site", **btn_style, command=add_site_gui)
btn_add.pack(pady=2)

# Botão para remover sites
btn_remove = tk.Button(root, text="Remover Site", **btn_style, command=remove_site_gui)
btn_remove.pack(pady=2)

# Botão para ativar o bloqueador
btn_activate = tk.Button(root, text="Ativar Bloqueador", **btn_style, command=activate_blocker_gui)
btn_activate.pack(pady=2)

# Botão para desativar o bloqueador
btn_deactivate = tk.Button(root, text="Desativar Bloqueador", **btn_style, command=deactivate_blocker_gui)
btn_deactivate.pack(pady=2)

# Botão para restaurar o arquivo hosts original
btn_restore = tk.Button(root, text="Restaurar Original", **btn_style, command=restore_original_gui)
btn_restore.pack(pady=2)

# Botão para sair do programa
btn_exit = tk.Button(root, text="Sair", **btn_style, command=root.quit)
btn_exit.pack(pady=2)

# Carrega os sites bloqueados do arquivo JSON
load_blocked_sites()
# Atualiza a ListBox com os sites carregados
update_listbox()
# Inicia o loop principal da interface gráfica
root.mainloop()