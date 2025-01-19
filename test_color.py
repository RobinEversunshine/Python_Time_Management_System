# import ui


try:
    import ui
    print("success")

except ImportError:
    print("error")



def display_colored_text():
    html = """

<style> body {font-size: 54px; font-family: Arial, sans-serif;} </style>

<p>•Secondary Study: <span style="color:#f44336;">0</span> hours <span style="color:#f44336;">5</span> minutes</p>
<p>    --Exercise: <span style="color:#f44336;">0</span> hours <span style="color:#f44336;">5</span> minutes</p>


<p>Useful Time Recorded:  <span style="color:#f44336;">0</span> hours <span style="color:#f44336;">26</span> minutes</p>
<p>All Time Recorded:  <span style="color:#f44336;">4</span> hours <span style="color:#f44336;">19</span> minutes</p>


"""
    # webview = ui.WebView(frame=(0, 0, 400, 400), background_color='white')
    webview = ui.WebView()
    webview.load_html(html)
    webview.present()

display_colored_text()



v = ui.View(frame=(0, 0, 400, 400), background_color='white')

# Create a label with larger text
label = ui.Label(frame=(50, 50, 300, 50))
label.text = "Hello, Pythonista!"
label.alignment = ui.ALIGN_CENTER
label.font = ('Helvetica', 36)  # Set font name and size

# Add label to the view
v.add_subview(label)

# Present the view
# v.present('sheet')

# print("\033[31mThis is red text\033[0m")


# from rich.console import Console
#
# console = Console()
# console.print("[red]This is red text[/red]")
# console.print("[green]This is green text[/green]")
# console.print("[yellow]This is yellow text[/yellow]")
#
# from rich import print
#
# print("Hello, [bold magenta]World[/bold magenta]!", ":vampire:", locals())
# from colorama import Fore, Style
#
# print(Fore.RED + "This is red text" + Style.RESET_ALL)
# print(Fore.GREEN + "This is green text" + Style.RESET_ALL)
# print(Fore.YELLOW + "This is yellow text" + Style.RESET_ALL)




