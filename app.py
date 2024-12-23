from flask import Flask, render_template, request
import json
import base64
import google.generativeai as genai
import markdown2
import io
import fitz

app = Flask(__name__)

genai.configure(api_key="AIzaSyAyBNKxzYNUGVEiF1mzVHDl48i8V6XBa-c")

model = 'gemini-1.0-pro' 
contents_b64 = 'W3sicm9sZSI6InVzZXIiLCJwYXJ0cyI6IjE1MDYgTG9tYmFyZCBTdC4g4paqIFNhbiBGcmFuY2lzY28sIENBIDk0MTIzIOKWqiAoOTI1KSA5MTUtMDYwOSDilqogdGltb3RoeWZlc3RhQHlhaG9vLmNvbVxuSElHSExZIFFVQUxJRklFRCBTQUxFUyBQUk9GRVNTSU9OQUxcbsOY74OYIFR3byB5ZWFycyBvZiBPcmFjbGUgZmllbGQgc2FsZXMgZXhwZXJpZW5jZSBhbmQgb3ZlciAxNiBtb250aHMgYXQgMiBuaW1ibGUgc3RhcnR1cHNcbsOY74OYIER5bmFtaWMgY29tbXVuaWNhdGlvbiwgY29uc3VsdGF0aW9uIGFuZCBwcmVzZW50YXRpb24gc2tpbGxzXG7DmO+DmCBCdWlsdCBzdHJvbmcgcmVsYXRpb25zaGlwcyB3aXRoIGtleSBJVCBkZWNpc2lvbiBtYWtlcnMgZnJvbSBzdGFydHVwcyB0byBGb3J0dW5lIDUwMCBjb21wYW5pZXNcbsOY74OYIENvbnNpc3RlbnRseSBhY2hpZXZlZCB5ZWFybHkgc2FsZXMgYnVkZ2V0cyBvdmVyICQxTU1cbsOY74OYIEV4Y2VsbGVudCBhYmlsaXR5IHRvIGNvbnNpc3RlbnRseSBtYWludGFpbiBjb21wb3N1cmUgYW5kIHJlbWFpbiBwcm9kdWN0aXZlIGluIGhpZ2gtcHJlc3N1cmUsIHRpbWVzZW5zaXRpdmVcbmVudmlyb25tZW50c1xuw5jvg5ggTWFuYWdlZCBhIHRlYW0gb2YgdHdvIHNhbGVzIHJlcHJlc2VudGF0aXZlc1xuUFJPRkVTU0lPTkFMIEVYUEVSSUVOQ0VcbkVudGVycHJpc2UgQWNjb3VudCBFeGVjdXRpdmUgSmFudWFyeSAyMDE1IC0gUHJlc2VudFxuVW5pb24gTWV0cmljcywgU2FuIEZyYW5jaXNjbywgQ0FcbsKn74KnIENsb3NlZCAxMyBkZWFscyB3aXRoaW4gZmlyc3QgMiBtb250aHMgb2Ygc3RhcnRpbmcgYW5kIG92ZXIgJDEwMCwwMDAgaW4gQVJSIGluIHRoZSBmaXJzdCA1IG1vbnRoc1xuwqfvgqcgRGV2ZWxvcGVkIGFuZCBpbXBsZW1lbnRlZCBzYWxlcyBwcm9jZXNzIHRvIGluY3JlYXNlIGNsb3NlIHJhdGlvIGZvciBlbnRpcmUgdGVhbVxuwqfvgqcgQnJvdWdodCBpbiBudW1lcm91cyBuZXQgbmV3IHdpbnMgYXQgRm9ydHVuZSA1MDAgY29tcGFuaWVzXG7Cp++CpyBOYXZpZ2F0ZWQgY29tcGxleCBzYWxlcyBjeWNsZSBiZXR3ZWVuIGFnZW5jaWVzIGFuZCBlbmQgdXNlcnNcblNNQiBBY3F1aXNpdGlvbiBBY2NvdW50IE1hbmFnZXIgTWFyY2ggMjAxNCDigJMgSmFudWFyeSAyMDE1XG5OZXcgUmVsaWMsIFNhbiBGcmFuY2lzY28sIENBXG7Cp++CpyBDb25zaXN0ZW50bHkgbGVhZCB0ZWFtIG9uIG9wZW5pbmcgbmV3IGFjY291bnRzXG7Cp++CpyBBdmVyYWdlZCA4IG5ldCBuZXcgd2lucyBwZXIgbW9udGggY2xvc2VkIDYgZGVhbHMgdGhlIGxhc3Qgd2VlayBpbiBEZWNlbWJlclxuwqfvgqcgQ2xvc2VkIG11bHRpcGxlIGFjY291bnRzIHdpdGggYW4gQVJSIG9mIG92ZXIgJDIwLDAwMCBhbmQgJDYwLDAwMCBvbiB0aGUgbGFzdCBkYXkgb2YgdGhlIHF1YXJ0ZXJcbsKn74KnIFRvcCBBY3F1aXNpdGlvbiBBY2NvdW50IE1hbmFnZXIgZm9yIHRoZSBtb250aCBvZiBOb3ZlbWJlclxuQWNjb3VudCBNYW5hZ2VyXG5PcmFjbGUgQ29ycG9yYXRpb24sIFJlZHdvb2QgU2hvcmVzLCBDQVxuRmllbGQgQWNjb3VudCBNYW5hZ2VyIEp1bHkgMjAxMyDigJMgTWFyY2ggMjAxNFxuwqfvgqcgRm91bmQgYW5kIGRyb3ZlIGEgJDEwTU0gb3Bwb3J0dW5pdHkgYXQgYSBnbG9iYWwgYmlvdGVjaG5vbG9neSBjb21wYW55XG7Cp++CpyBDbG9zZWQgZmlyc3QgZGVhbCB3aXRoaW4gOTAgZGF5cyBvZiBzdGFydCBkYXRlXG7Cp++CpyBTZXR1cCBmaW5hbmNpYWwgc29mdHdhcmUgcHJvdmlkZXIgYXMgYSBtYW5hZ2VkIHNlcnZpY2UgcHJvdmlkZXIsIHRvIGNyZWF0ZSBhbiBydW4gcmF0ZSBhY2NvdW50XG5FbWVyZ2luZyBNYXJrZXRzIEFjY291bnQgTWFuYWdlciBKdW5lIDIwMTIg4oCTIEp1bHkgMjAxM1xuwqfvgqcgMTE1JSBncm93dGggZm9yIGN1cnJlbnQgdGVycml0b3J5LCBjbG9zZWQgb3ZlciA2MDBLIGluIGZpcnN0IDYgbW9udGhzXG7Cp++CpyBPcmdhbml6ZWQgbnVtZXJvdXMgdGVjaCBkYXlzLCByb2FkbWFwIGRpc2N1c3Npb25zIGFuZCBzb2x1dGlvbiBjZW50ZXIgdmlzaXRzXG7Cp++CpyBBcmNoaXRlY3RlZCBuZXcgZGF0YSBjZW50ZXIgZm9yIGNoZWNrIGltYWdpbmcgY29tcGFueVxuwqfvgqcgTnVtZXJvdXMgbmV3IHNlcnZlciBhbmQgc3RvcmFnZSB3aW5zXG7Cp++CpyBTdHJhdGVnaWMgcmVsYXRpb25zaGlwIHdpdGggQ0VP4oCZcyBpbiA1IE1pZHdlc3Qgc3RhdGVzIChNTiwgSUEsIE1PLCBXSSAmIFRYKVxuRW50ZXJwcmlzZSBBY2NvdW50IE1hbmFnZXIgQXVndXN0IDIwMTAg4oCTIE1heSAyMDEyXG7Cp++CpyBGb3VyIGNvbnNlY3V0aXZlIHF1YXJ0ZXJzIG9mIHF1b3RhIGFjaGlldmVtZW50LCBGWTEyIHF1b3RhIGFjaGlldmVtZW50XG7Cp++CpyBUb3AgRHJpdmVyIG9mIHRoZSBxdWFydGVyIFExIEZZMTJcbsKn74KnIEZZIDExIGJyaWRnaW5nIGxlYWRlciBmb3IgaGFyZHdhcmUsIHN1Y2Nlc3NmdWxseSBwYXNzZWQgJDUwMCwwMDAgaW4gc29mdHdhcmUgb3Bwb3J0dW5pdGllc1xuwqfvgqcgRWZmZWN0aXZlbHkgbWFuYWdlZCBtdWx0aXBsZSBwYXJ0bmVyIHJlbGF0aW9uc2hpcHMgYW5kIGNyb3NzIGZ1bmN0aW9uYWwgdGVhbXMgdG8gZHJpdmUgYnVzaW5lc3NcbkVEVUNBVElPTlxuQmFjaGVsb3Igb2YgQXJ0cyDigJMgQnVzaW5lc3MvRWNvbm9taWNzLCBVbml2ZXJzaXR5IG9mIENhbGlmb3JuaWEsIFNhbnRhIEJhcmJhcmEsIENBIDIwMDUgICAgICAgICAgICAgICAgICAgIHRoaXMgaXMgcmVzdW1lIG9mIGNhbmRpZGF0ZS4gc2hvdyBoaWdobGlnaHRzIGFjaGl2ZW1lbnQgb2YgaGlzIn0seyJyb2xlIjoibW9kZWwiLCJwYXJ0cyI6IiMjIEhpZ2hsaWdodHMgb2YgQ2FuZGlkYXRlJ3MgQWNoaWV2ZW1lbnRzOlxuXG4qKk92ZXJhbGw6KipcblxuKiAqKkhpZ2hseSBzdWNjZXNzZnVsIHNhbGVzIHByb2Zlc3Npb25hbCB3aXRoIGNvbnNpc3RlbnQgdHJhY2sgcmVjb3JkIG9mIGV4Y2VlZGluZyBxdW90YXMgYW5kIGRyaXZpbmcgcmV2ZW51ZSBncm93dGguKipcbiogKipFeHBlcmllbmNlIHNlbGxpbmcgZm9yIGJvdGggZXN0YWJsaXNoZWQgY29tcGFuaWVzIGxpa2UgT3JhY2xlIGFuZCBuaW1ibGUgc3RhcnR1cHMuKipcbiogKipTdHJvbmcgcmVsYXRpb25zaGlwIGJ1aWxkZXIgd2l0aCBrZXkgZGVjaXNpb24gbWFrZXJzIGluIHZhcmlvdXMgc2l6ZWQgY29tcGFuaWVzLioqXG4qICoqRWZmZWN0aXZlIGxlYWRlciBhbmQgdGVhbSBwbGF5ZXIuKipcblxuKipTcGVjaWZpYyBBY2hpZXZlbWVudHM6KipcblxuKiAqKlVuaW9uIE1ldHJpY3M6KiogXG4gICAgKiBDbG9zZWQgMTMgZGVhbHMgd2l0aGluIGZpcnN0IDIgbW9udGhzIGFuZCBvdmVyICQxMDAsMDAwIGluIEFSUiBpbiB0aGUgZmlyc3QgNSBtb250aHMuXG4gICAgKiBEZXZlbG9wZWQgYW5kIGltcGxlbWVudGVkIGEgc2FsZXMgcHJvY2VzcyB0aGF0IGluY3JlYXNlZCBjbG9zZSByYXRpbyBmb3IgdGhlIGVudGlyZSB0ZWFtLlxuICAgICogU2VjdXJlZCBudW1lcm91cyBuZXQgbmV3IHdpbnMgYXQgRm9ydHVuZSA1MDAgY29tcGFuaWVzLlxuKiAqKk5ldyBSZWxpYzoqKiBcbiAgICAqIENvbnNpc3RlbnRseSBsZWQgdGVhbSBpbiBvcGVuaW5nIG5ldyBhY2NvdW50cy5cbiAgICAqIEF2ZXJhZ2VkIDggbmV0IG5ldyB3aW5zIHBlciBtb250aCBhbmQgY2xvc2VkIDYgZGVhbHMgaW4gdGhlIGxhc3Qgd2VlayBvZiBEZWNlbWJlci5cbiAgICAqIENsb3NlZCBtdWx0aXBsZSBhY2NvdW50cyB3aXRoIHNpZ25pZmljYW50IEFSUiwgaW5jbHVkaW5nIG9uZSBmb3IgJDYwLDAwMCBvbiB0aGUgbGFzdCBkYXkgb2YgdGhlIHF1YXJ0ZXIuXG4gICAgKiBSZWNvZ25pemVkIGFzIFRvcCBBY3F1aXNpdGlvbiBBY2NvdW50IE1hbmFnZXIgZm9yIE5vdmVtYmVyLlxuKiAqKk9yYWNsZSBDb3Jwb3JhdGlvbjoqKiBcbiAgICAqIElkZW50aWZpZWQgYW5kIGRyb3ZlIGEgJDEwTU0gb3Bwb3J0dW5pdHkgYXQgYSBnbG9iYWwgYmlvdGVjaG5vbG9neSBjb21wYW55LlxuICAgICogQ2xvc2VkIGZpcnN0IGRlYWwgd2l0aGluIDkwIGRheXMgb2Ygc3RhcnRpbmcuXG4gICAgKiBFc3RhYmxpc2hlZCBhIGZpbmFuY2lhbCBzb2Z0d2FyZSBwcm92aWRlciBhcyBhIG1hbmFnZWQgc2VydmljZSBwcm92aWRlciwgY3JlYXRpbmcgYSByZWN1cnJpbmcgcmV2ZW51ZSBzdHJlYW0uXG4gICAgKiBBY2hpZXZlZCAxMTUlIGdyb3d0aCBmb3IgYXNzaWduZWQgdGVycml0b3J5IGFuZCBjbG9zZWQgb3ZlciAkNjAwSyBpbiB0aGUgZmlyc3QgNiBtb250aHMuXG4gICAgKiBBcmNoaXRlY3RlZCBhIG5ldyBkYXRhIGNlbnRlciBmb3IgYSBjaGVjayBpbWFnaW5nIGNvbXBhbnkgYW5kIHNlY3VyZWQgbnVtZXJvdXMgc2VydmVyIGFuZCBzdG9yYWdlIHdpbnMuXG4gICAgKiBCdWlsdCBzdHJhdGVnaWMgcmVsYXRpb25zaGlwcyB3aXRoIENFT3MgaW4gNSBNaWR3ZXN0IHN0YXRlcy5cbiAgICAqIEFjaGlldmVkIGZvdXIgY29uc2VjdXRpdmUgcXVhcnRlcnMgb2YgcXVvdGEgYWNoaWV2ZW1lbnQgYW5kIHJlY29nbml6ZWQgYXMgVG9wIERyaXZlciBvZiB0aGUgcXVhcnRlci5cbiAgICAqIFN1Y2Nlc3NmdWxseSBicmlkZ2VkIG92ZXIgJDUwMCwwMDAgaW4gc29mdHdhcmUgb3Bwb3J0dW5pdGllcy5cblxuKipBZGRpdGlvbmFsIFNraWxsczoqKlxuXG4qIER5bmFtaWMgY29tbXVuaWNhdGlvbiwgY29uc3VsdGF0aW9uLCBhbmQgcHJlc2VudGF0aW9uIHNraWxscy5cbiogQWJpbGl0eSB0byBtYW5hZ2UgYW5kIG1vdGl2YXRlIHRlYW1zLlxuKiBQcm92ZW4gc3VjY2VzcyBpbiBuYXZpZ2F0aW5nIGNvbXBsZXggc2FsZXMgY3ljbGVzLlxuKiBIaWdobHkgYWRhcHRhYmxlIGFuZCB0aHJpdmVzIGluIGhpZ2gtcHJlc3N1cmUsIHRpbWUtc2Vuc2l0aXZlIGVudmlyb25tZW50cy5cblxuVGhpcyBjYW5kaWRhdGUgZGVtb25zdHJhdGVzIGEgc3Ryb25nIHRyYWNrIHJlY29yZCBvZiBzdWNjZXNzIGluIHZhcmlvdXMgc2FsZXMgcm9sZXMgYW5kIHBvc3Nlc3NlcyB2YWx1YWJsZSBza2lsbHMgdGhhdCB3b3VsZCBiZW5lZml0IGFueSBvcmdhbml6YXRpb24uIn1d' # @param {isTemplate: true}
generation_config_b64 = 'eyJ0ZW1wZXJhdHVyZSI6MC45LCJ0b3BfcCI6MSwidG9wX2siOjEsIm1heF9vdXRwdXRfdG9rZW5zIjoyMDQ4LCJzdG9wX3NlcXVlbmNlcyI6W119' # @param {isTemplate: true}
safety_settings_b64 = 'W3siY2F0ZWdvcnkiOiJIQVJNX0NBVEVHT1JZX0hBUkFTU01FTlQiLCJ0aHJlc2hvbGQiOiJCTE9DS19NRURJVU1fQU5EX0FCT1ZFIn0seyJjYXRlZ29yeSI6IkhBUk1fQ0FURUdPUllfSEFURV9TUEVFQ0giLCJ0aHJlc2hvbGQiOiJCTE9DS19NRURJVU1fQU5EX0FCT1ZFIn0seyJjYXRlZ29yeSI6IkhBUk1fQ0FURUdPUllfU0VYVUFMTFlfRVhQTElDSVQiLCJ0aHJlc2hvbGQiOiJCTE9DS19NRURJVU1fQU5EX0FCT1ZFIn0seyJjYXRlZ29yeSI6IkhBUk1fQ0FURUdPUllfREFOR0VST1VTX0NPTlRFTlQiLCJ0aHJlc2hvbGQiOiJCTE9DS19NRURJVU1fQU5EX0FCT1ZFIn1d' # @param {isTemplate: true}
user_input_b64 = '' 

contents = json.loads(base64.b64decode(contents_b64))
generation_config = json.loads(base64.b64decode(generation_config_b64))
safety_settings = json.loads(base64.b64decode(safety_settings_b64))
user_input = base64.b64decode(user_input_b64).decode()
stream = False

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/predict', methods=['POST'])
def predict_resume():
    file = request.files['file']
    prompt1 = request.form['prompt1']
    prompt2 = request.form['prompt2']

    
    pdf_content = file.read()
    doc = fitz.open(stream=pdf_content, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    user_input = text + prompt1 + prompt2


    gemini = genai.GenerativeModel(model_name=model)
    chat = gemini.start_chat(history=contents)
    response = chat.send_message(user_input, stream=stream)
    display = markdown2.markdown(response.text)
    return render_template('result.html', result=display)

if __name__ == '__main__':
    app.run(debug=True)
