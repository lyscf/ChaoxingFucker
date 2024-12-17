# Chaoxing Fucker

帮助你在期末复习过程中快速下载老师上传的课件和网课

## How to use

在你的课程主页url里面有一个 courseid ，复制并修改程序里面的，然后把你的cookie也填写进去

程序默认只帮你下载PDF文件

注意 这些 **文件和视频** 的 **下载链接** 都需要携带Refer头，否则会403,我没写脚本 但是在这里给出一个示例命令来下载文件

```
curl "YourDownloadURL" -H "Accept: */*" -H "Referer: https://mooc1.chaoxing.com/ananas/modules/video/index.html?v=2024-1128-1842" -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36" --output 1.docx
```


