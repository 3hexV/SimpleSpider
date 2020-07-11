# Simple Spider(易爬虫)

- 这是什么：
这是一个**简单上手**的，使用**简单配置**，即可实现**文本数据爬取**，**文件下载**，**图片下载**的爬虫脚本，并且支持**多种提取方式**，数据可以直接保存到数据库(现阶段仅支持MongoDB)，有**一定的数据处理**能力。
- 使用者的基本要求：
- 了解网页的**基本结构**
- 熟悉网页的**请求**原理
- 会使用简单的**XPath定位元素**
- 会使用**正则提取**数据
- 会使用**json**做简单配置
- 使用流程图：

![使用流程图](http://39.107.227.91/ss_info/ss_img/flow.png)

- 支持的功能：
[Function Desc](Function.md)

## 1.目录介绍
##### [Dir Desc](Dir.md)

## 2.环境配置
- python(3.6.5)
- mongodb(如果你需要数据直接保存到mongodb中)
- Visual Studio Code(编辑json和配置文件，也可以使用其他软件代替)
- Google Chrome/FireFox(谷歌浏览器或者火狐)

1. 准备
依次按照上述软件，并完成环境配置。
2. 安装依赖
打开爬虫根目录env_int文件夹，安装依赖库：
在windows平台上，可以直接运行env_ini.bat文件，或者使用（liunx平台上同样适用这个命令）。
```cmd
pip install -r pack.txt
```
3. 确认
使用默认的模板文件测试。
在爬虫根目录运行start.py，查看user_config/test/中是否出现testRes.json文件。

## 3.模板介绍
我们**默认**使用的是：

- 一般通用爬虫(general) 
[爬取**自定义数量**、**自定义规则**的文本数据]

同时爬虫脚本中，提供了几种**专用爬虫**：

- URL专用爬虫(URL) 
[爬取页面中的**所有URL**/**用户指定的URL**]
- 文本专用爬虫(text) 
[爬取页面中的**所有文本**/**用户指定的一个规则文本**]
- 文件专用爬虫(file) 
[爬取页面中的**所有文件**/**用户指定的文件**]
- 图片专用爬虫(img) 
[爬取页面中的**所有图片**/**用户指定的图片**]

在**user_config/moban/**中的5个json文件，为5个配置模板，依次对应如下：
- config_1.json >> 一般通用爬虫(general)
- config_2.json >> URL专用爬虫(URL)
- config_3.json >> 文本专用爬虫(text)
- config_4.json >> 图片专用爬虫(img)
- config_5.json >> 文件专用爬虫(file)

同时在每个配置文件的**"Stype"**属性中可以看出它的类型。

## 4.流程介绍
一般的爬取流程如下：
1. 分析 (分析目标站点[URL结果，网页请求方法，网页的结果，数据来源等])
2. 测试 (测试配置文件的爬取结果)
3. 运行 (编写爬虫流程文件，运行爬虫，得到结果)

### 1.分析
> 每次启动爬虫，都会**缓存目标网址**的内容。保存再**result/cache_page/**中，以**请求的URL**名命名。在这里打开缓存网页，使用浏览器的检查功能定位需要的元素位置。

这是学习爬虫的基本技能，不在赘述。
### 2.测试
> 在**user_config/**中有一个**test**文件夹，爬虫脚本每次启动都会检查，这个文件中是否有除了**testRes.json**(这是固定生成的**测试结果文件**)文件以外的**其他json**，如果存在，就将它作为测试的json文件解析，并运行爬虫，进入**测试模式**。没有则进入**运行模式**。

测试时，只需将你要测试的json文件**复制/移动**到**test/**文件夹中，再运行爬虫即可。
返回的数据再**test/**下的**restRes.json**中。
其中，如果是**测试下载功能**，保存的文件在**result/data/文件夹** (文件夹=爬取的类型(FILE/IMG)_目标网址的域名)

### 3.运行
> 所有的配置文件**必须在/user_config/**中(在**/user_config/test/中不能有配置文件**)，并配置好proSpider.desc文件，启动爬虫即可。同时在**一个流程中有多个爬虫**时，后面的爬虫**按照顺序**依次将json中的**flow_input**属性置为**link**。

首先将测试好的json配置文件全部放在/user_config/中。
下面开始配置proSpider.desc文件，文件一般如下：
```
# 新建爬虫
newSpider(1, config_1.json)

# 新建爬虫流程
newDescFlow(1, 1)

# 数据保存方式
save(1, mongo(res.json))
```

**newSpider(spiderName, spiderConfigFileName)**:
- 功能：
新建一个爬虫。
- spiderName：
这个爬虫的名字。例如：spider1。
- spiderConfigFileName：
这个爬虫的配置文件的名字（必须在/user_config/中）。

**newDescFlow(FlowName, FlowDesc)**:
- 功能：
新建一个爬虫流程。
- FlowName：
流程名。例如：Flow1。
- FlowDesc：
流程的描述。例如：spider1-spider2-spier3（**使用-分开每个爬虫**）

**save(FlowName, SaveFunc)**
- 功能：
定义某个流程执行后，数据保存的方式
- FlowName：
流程名。例如：Flow1。
- SaveFunc：
流程的描述。例如：save(1, json(res.json))，
save(1, mongodb(spiderHub.dataHub0))

在proSpider.desc中，先**新建爬虫，然后新建爬虫的流程，再定义每个流程保存数据的方式**。

## 5.实例

### 1.某易新闻爬取
[实例1](http://39.107.227.91/2019/12/07/simplespider-v2-0%e7%88%ac%e5%8f%96%e6%9f%90%e6%98%93%e6%96%b0%e9%97%bb/#more-854)

### 2.某库图片下载

### 3.某校文件下载

## 6.详细介绍
### 1.系统配置文件详细介绍（.ini文件）

- **spiderBaseConfig.ini**
- 位置：
/simple_spider/spider_lib/
- 功能：
配置爬虫工作时的一些配置
- 详细:
	- UA：
	配置爬虫使用的UA方式。
	- DefEncoding：
	请求网页可能用的编码。当用户自定义编码，这项配置失效。
	- DefEncodingNoFound：
	当网页的编码不再DefEncoding中，或者没有找到编码，并且用户没有使用强制编码，强制使用该编码。当用户自定义编码，这项配置失效。
	- CacheSitePage：
	是否缓存每次请求的网页。true：是，false“否。
	- DefPageSuffix：
	缓存相关配置，当你缓存的网页后缀名和实际不同，在这里添加你想要的即可。
	- ExtractFuncName：
	定义支持的**数据提取**的方法名
	- DataHandleFuncName：
	定义支持的**数据处理**的方法名
	- ReDefLinkSymbol：
	在数据处理时，使用正则提取有多个提取结果后，采用的默认连接字符。\sp代表空格，\n 换行，\t Tab，\N 表示空，以及其他字符。
	- DataListToStr：
	当使用处理字符串的函数，去处理字符串数组时。true：将数组转为字符串处理，false：对数据中的字符串遍历处理，不转为字符串。
	- ThreadNumber：
	爬虫的工作线程数量。
	- ThreadSleepTime：
	爬虫的每个线程的休眠时，单位ms。
	- F_FILE_Spider_Suffix：
	文件专用爬虫默认爬取的文件类型。
	- F_IMG_Spider_Suffix：
	图片专用爬虫默认爬取的图片类型。
	- F_URL_Spider_Suffix：
	URL专用爬虫默认爬取的URL类型。
	- F_FILE_DOWNLOAD_URL：
	文件下载时，对提取到文件URL处理方式(URL拼接方式)。@DY(domainName)提取顶级域名，拼接在它的前面；@NP(now page)，当前位置url拼接在它的前面；@L+XX，在左边拼接XX；@R+XX 在右边拼接XX
	- NoSpiderTip：
	是否屏蔽爬虫运行时的大部分提示信息（不能屏蔽日志）。true：屏蔽，false：否。
	- mongodbHost：
	mongodb的连接IP地址（默认127.0.0.1）
	- mongodbPort：
	mongodb的工作端口（默认27017）
- **syspath.ini**
- 位置：
/simple_spider/sys_func/
- 功能：
爬虫运行的基本路径配置。
- 详细：
这里没有用户需要自定义配置的地方（请勿修改）。

### 2.爬虫工作配置文件（.json文件）
> 这里以通用爬虫为例，其他的专用爬虫会有些区别，其中也会叙述。

```
{
"Stype": "general",
"url": ["https://www.ex.com/news/", []],
"headers": {}, 
"post_data": {},
"field": {
"*title": [
    ["xpath", "//td[@class=\"c_title\"]//text()"],
    [["list_to_str", ""]]
],
"*url": [
    ["xpath", "//td[@class=\"content\"]//p//text()"],
    [["list_to_str", "\n"]]
],
"id": [
    ["num_change", 1,300,1,0],
    []
]
},
"ex": [[], "", ""],
"flow_input": "",
"flow_output": ""
}
```
----
:heavy_exclamation_mark: **注意**：由于这里使用json文件配置爬虫的工作信息，所以里面的部分符号，需要转义。
例如：**在引号[ " ]，反斜杠[ \ ]，小括号[ ( ]等前面加上一个反斜杠[ \ ]**。具体的和正则的匹配使用的转义方法差不多。

- **Stype**:
爬虫的类型。可以为general,url,text,f_file,f_img。类型与其名字同义。
- **url**:
URL的拼接规则。格式：["url模板",[具体的拼接方法]]。
1. **使用单一的url，不拼接**
在url模板处直接写url即可。
例如：
`["https://www.ex.com/news/", []]`或者
`["https://www.ex.com/news/"]`。
后面的拼接方法写不写都可以。
2. ** 使用的ulr需要数值拼接**
在url模板出写入一个url例子，然后将需要数值替换的写出[P1]，再在后面写方法。
例如：
`["https://www.ex.com/news/news_id_123[P1]", ["num_change", 0,200,1,3]]`
这里[P1]的位置将会被数值字符串"000"到"200"替换，构成201个url。
**num_change的参数：起始数值，最大数值（包括自身），步长，字符长度。**
3. ** 使用的ul来源于文件**
在url模板中直接写入[P1]，在后面写入方法。
例如：
`["[P1]", ["text_read", "url.txt", ""]]]`
这里url.txt文件必须在/user_config/res/中，并且url.txt得到每个url以换行分割。
**text_read的参数：文件位置(/user_config/res/中)，文件编码（默认都是utf-8-sig）**
- **headers**:
爬虫的请求头。
这里如果用户没指定User-Agent，爬虫会自动生成UA。
同时cookie等请求头参数添加在这里即可。例如：
```
{
"cookie":"BD_UPN=12314753;BDUSS=HY2LW04cUVabzFxZ3NGLTNDSWdvcThrdFJVdlAxQ3NmRVNDVTIwblZmUkxYQVZAEvP3V1Lz91da;"
}
```
:triangular_flag_on_post: **如果使用自定义的UA库。请在spiderBaseConfig.ini配置中将UA置为2，并将自定义的UA库复制到/simple_spider/res/UA.txt中。**
- **post_data**：
post请求参数
例如
```
{
"id": "123",
"index": "456"
}
```
- **field**:
爬虫爬取的数据爬取方式描述。
结果如下：
```
"字段名称":[
["数据的提取方式","参数"...],
[["数据提取后的处理方式1","参数"...],["数据提取后的处理方式2","参数"...]]
]
```
**其中的对于字段名，如果在字段名前加上 * (星号)，则表示该字段不能为空，在数据提取时，该字段为空，爬虫会丢弃该条记录。**

:triangular_flag_on_post: 对于专用爬虫，他们字段名固定，并且只能为一个。详细如下：

| 爬虫类型     |  数据提取  |                  数据处理                   | 是否可以自定义字段名和字段数量 |
| :----------- | :--------: | :-----------------------------------------: | :----------------------------: |
| 一般通用爬虫 | :heavy_check_mark: |     :heavy_check_mark:  |     :heavy_check_mark:        |
| URL专用爬虫  |:heavy_check_mark:| :heavy_multiplication_x: 使用ex属性的第2个参数实现url处理 |    :heavy_multiplication_x: 强制为一个URL    |
| 文本专用爬虫 | :heavy_check_mark: |           :heavy_check_mark:   |   :heavy_multiplication_x: 强制为一个TEXT    |
| 文件专用爬虫 |:heavy_check_mark: | :heavy_multiplication_x: 使用ex属性的第2个参数实现url处理 |  :heavy_multiplication_x: 强制为一个F_FILE   |
| 图片专用爬虫 | :heavy_check_mark: | :heavy_multiplication_x: 使用ex属性的第2个参数实现url处理 |   :heavy_multiplication_x: 强制为一个F_IMG   |

**数据处理方式是，单向的、流程式的**。
`处理方式1->处理方式2->处理方式3`

数据提取方式：
	1. ["xpath","xpath规则"]
	["xpath", "//div[@class=\"content\"]//p/text()"]

	2. ["re","正则表达式","拼接规则"]
	["re","title:(.\*?)\"\s\*author:(.\*?)\"", "[P1]--[P2]"]
	(每一个[Pn]代表一个()匹配到结果，拼接规则为空，爬虫会依据spiderBaseConfig.ini中的ReDefLinkSymbol参数完成拼接)

	3. ["json","参数1"..."参数n"]
	["json", "data", 2, "desc", "name"]
	等价于aim_data["data"][2]["desc"]["name"]的字典选择方式
	这里参数为字符时表示键值，为数值时表示该数组的第n个。连续向下选择。


数据处理方式：
	1.["text_replace", "替换前字符串", "替换后的字符串"]
	["text_replace", "\n", " "]
	将数据中的\n全部取出。如果数据为list（列表类型)，
	那么会**根据spiderBaseConfig.ini中的DataListToStr参数**来决定，
	是否先转为字符串，处理；还是遍历列表处理每个字符串。

	2.["text_sub", "开始字符串", "结尾字符串"(包含本身)]
	["text_sub", "start", "stop"]
	这里如果开始字符串为空，表示从头开始；结尾字符串为空，表示到尾结束
	**这里的提取，会包含结尾字符串。**

	3. ["list_to_str","分隔符"]
	["list_to_str", "\n"]
	将列表转为字符串，并以分割符，分割每个列表数据。（一般用于正文保留分段信息）

	4. ["text_strip","l|r|lr"]
	["text_strip", "l"]
	去除文本的左边空格，同理，r代表右边；lr代表左右两边。

	5. ["re_handle","正则表达式","拼接规则"]
	和数据提取中的re一样，只是名称不一样。

例如使用以下配置:
```
"field": {
"*title": [
    ["xpath", "//td[@class=\"c_title\"]//text()"],
    [["list_to_str", ""]]
],
"*url": [
    ["xpath", "//td[@class=\"content\"]//p//text()"],
    [["list_to_str", "\n"]]
],
"*id": [
    ["num_change", 1,300,1,0],
    []
]
},
```

- **ex**:
参数样式：
[[文件/图片的后缀(类型)], "URL拼接规则", "强制编码"]
这个参数仅对url专用爬虫，文件下载爬虫，图片下载爬虫有效。如下表(ex参数控制表):

| 爬虫类型     | 文件/图片的后缀(类型) | URL拼接规则 |  强制编码  |
| :----------- | :-------------------: | :---------: | :--------: |
| 一般通用爬虫 |      :heavy_multiplication_x:       | :heavy_multiplication_x:  | :heavy_check_mark: |
| URL专用爬虫  |     :heavy_check_mark: | :heavy_check_mark:  | :heavy_check_mark: |
| 文本专用爬虫 |      :heavy_multiplication_x:       | :heavy_multiplication_x:  | :heavy_check_mark: |
| 文件专用爬虫 |      :heavy_check_mark:       | :heavy_check_mark:  | :heavy_check_mark: |
| 图片专用爬虫 |      :heavy_check_mark:      | :heavy_check_mark: | :heavy_check_mark: |

:heavy_check_mark: 表示有效控制 :heavy_multiplication_x:  表示无效控制


- **flow_input**:
爬虫的输入流，用于连接爬虫，形成爬虫的工作流程。
参数：空或者link
当为空时，url起作用，使用url属性构建的url；
当为link时，url不起作用，失效。url来源于前一个爬虫的flow_output
- **"flow_output"**:
爬虫的输出流，用于输出爬虫的爬取数据的**某一类数据**，作为**下一个爬虫的url**输入(**flow_input必须置为"link"，才可以接收到**)。例如：title_url

:triangular_flag_on_post:这个属性对不同爬虫的，作用范围如下表：

| 爬虫类型     | flow_output | other                                   |
| :----------- | :---------: | :-------------------------------------- |
| 一般通用爬虫 | :heavy_check_mark:  | 输出用户配置的字段名（请输出url一类的） |
| URL专用爬虫  | :heavy_multiplication_x: | 强制输出URL                             |
| 文本专用爬虫 | :heavy_multiplication_x:  | 无输出                                  |
| 文件专用爬虫 | :heavy_multiplication_x:  | 无输出                                  |
| 图片专用爬虫 | :heavy_multiplication_x:  | 无输出                                  |

:heavy_check_mark: 表示有效控制 :heavy_multiplication_x: 表示无效控制
