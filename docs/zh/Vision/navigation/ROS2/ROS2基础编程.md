# ROS2基础编程

​	（1）**面向对象编程**

​	面向对象的语言都可以创建类，所谓的类就是对事物的一种封装

```
#include ＜string＞
#include "rclcpp/rclcpp.hpp"
class PersonNode : public rclcpp::Node
{
private:
	std::string name_;
	int age_;
public:
	PersonNode（const std::string &node_name,
		const std::string &name,
		const int &age） : Node（node_name）
{
	this-＞name_ = name;
	this-＞age_ = age;
};
void eat（const std::string &food_name）
{
	RCLCPP_INFO（this-＞get_logger（）, " 我是 %s，今年 %d 岁，我现在正在吃 %s",
		name_.c_str（）, age_, food_name.c_str（））;
	};
};
int main（int argc, char ＊＊argv）
{
	rclcpp::init（argc, argv）;
	auto node = std::make_shared＜PersonNode＞（"cpp_node", " 法外狂徒张三 ", 18）;
	node-＞eat（" 鱼香 ROS"）;
	rclcpp::spin（node）;
	rclcpp::shutdown（）;
	return 0;
}
```

解释：

- class PersonNode : public rclcpp::Node

​	：是继承符号，public是访问说明符，rclcpp::Node是基类。

​	标识PersonNode类以public方式继承自rclcpp::Node类

- private
  - 这部分代码开始定义PersonNode类的私有成员区域，私有成员只能在类内部访问（例如可以在类的内部调用私有函数，但是不能再外部比如main函数调用私有函数，会报错）

- RCLCPP_INFO()
  - 宏记录一条日志信息（是rclcpp库中的）
  - this->get_logger()
    - this是C++中的一个关键字，指向当前对象（即调用成员函数的那个对象）
    - get_logger()是rclcpp::Node类的一个成员函数，用于获取当前节点的日志记录器对象
- rclcpp::init
  - rclcpp::init函数初始化ROS2系统
- auto node = std::make_shared<PersonNode>()
  - auto 是类型推导关键字，当使用auto声明变量时，编译器会根据变量的初始化表达式自动推断其类型
  - std::make_shared是C++标准库<memory>头文件中的一个函数模板，用于在堆上分配对象并返回一个std::shared_ptr智能指针来管理该对象。std::shared_ptr是一种智能指针，它会自动管理所指向对象的生命周期，当没有任何std::shared_ptr指向该对象时，对象会被自动释放，从而避免了内存泄露的问题
  - <PersonNode>指向的是PersonNode类，不是成员函数PersonNode
- rclcpp::spin(node)
  - 使程序进入事件循环，等待并处理ROS2的各种事件，直到节点被关闭或遇到其他终止条件才会结束（例如ctrl+c中断信号）
- std
  - std::string可以直接使用，因为包含了<string>头文件
  - std::make_shared（被定义在<memory>头文件中）可以直接使用，因为rclcpp/rclcpp.hpp这个头文件可能间接包含了<memory>头文件

- c_str()
  - c_str()是std::string类的一个成员函数
  - c_str()的作用是返回一个指向以空字符”\0"结尾的字符数组的指针，这个字符数组包含了std::string对象中的内容。简单来说，它把std::string对象转换为C风格的字符串（也就是以'\0'结尾的字符数组）
  - 使用std::string 都要使用.c_str()（平常是使用流操作符（<<）


  ​	（2）**C++新特性**

  ​	-1 自动类型推导（python是eval()）

  ​	auto关键字，它可以在给变量赋值时根据等号右边返回的类型自动推导变量的类型

  ​	-2 智能指针

  ​	可以动态分配内存，避免内存泄漏和空指针等问题。三种类型的智能指针：std::unique_ptr、std::shared_ptr 和std::weak_ptr。该指针会记录指向同一个资源的指针数量，当数量为 0 时会自动释放内存，这样一来就不会出现提前释放或者忘记释放的情况。

  ​	智 能 指 针 是 在 头 文 件 ＜memory＞ 的 std 命 名 空 间 中 定 义 的

  ​	-3 Lambda表达式	

  ```
[capture list]（parameters） -＞ return_type { function body }
  ```

  ​	Lambda 表达式是 C++11 引入的一种匿名函数，没有名字，但是也可以像正常函数一样调用。capture list 表示捕获列表，可以用于捕获外部变量；parameters 表示参数列表；return_type 表示返回值类型；function body 表示函数体

  ​	Lambda语法需要导入algorithm库（#include<algorithm>）

  ​	-4 函数包装器 std::function

  ​	std::function 是 C++11 引入的一种通用函数包装器，它可以存储任意可调用对象（函数、函数指针、Lambda 表达式等）并提供统一的调用接口

  ​	＜functional＞ 是函数包装器所在的头文件.。在外部定义的函数称为自由函数

  ​	std::function＜void（const std::string &）＞ 对象。示例：

  ```
	std::function＜void（const std::string &）＞ save3 = std::bind（&FileSave::save_with_member_fun, &file_save, std::placeholders::_1）;
  ```

  - 解释：
    - std::function是C++标准库中的一个通用多态函数包装器，它可以存储、复制和调用任何可调用对象
    - <void(const std::string &)>是std::function的模板参数，指定了所包装的可调用对象的签名
    - std::bind可以将成员函数变成一个std::function的对象，正常调用成员函数的方法是使用对象加函数的形式，如file_save.save_with_member_fun，这里用std::bind将成员函数FileSave::save_with_member_fun与对象file_save绑定在一起，并使用std::placeholder::_1占位符预留一个位置传递函数的参数
    - std::placeholders::_1是第一个占位符标识，在调用绑定的函数时，传入的第一个参数将被传递给save_with_member_fun函数。也就是说，当调用saves3时，传入的参数会被转发给FileSave::save_with_member_fun函数
    - **&通常紧跟在类型名之后，写在变量名之前**
    - 需要导入functional这个库（#include<functional>），才能使用函数包装起std::function

  ​	（3）**多线程与回调函数**

  - python

  ```
import threading
import requests
class Download:
    def download(self, url, callback):
        print(f' 线程 :{threading.get_ident()} 开始下载：{url}')
        response = requests.get(url)
        response.encoding = 'utf-8'
        callback(url, response.text)
    def start_download(self, url, callback):
        thread = threading.Thread(target=self.download, args=(url, callback))
        thread.start()
def download_finish_callback(url, result):
    print(f'{url} 下载完成，共：{len(result)} 字，内容为：{result[:5]}...')
def main():
    d = Download()
    d.start_download('http://localhost:8000/novel1.txt', download_finish_callback)
    d.start_download('http://localhost:8000/novel2.txt', download_finish_callback)
    d.start_download('http://localhost:8000/novel3.txt', download_finish_callback)

  ```

  ```
注意：thread = threading.Thread(target=self.download, args=(url, callback))
  ```

  ​	python3 -m http.server可以启动一个本地的HTTP服务器（在哪个目录下输入这个命令，启动的服务器地址也是有区别的，只能找到该文件夹里面的内容）

  - C++

  - ```
    #include <iostream>
    #include <thread>
    #include <chrono>
    #include <functional>
    #include <cpp-httplib/httplib.h>
    
    class Download {
    public:
        void download(const std::string &host, const std::string &path, const std::function<void(const std::string &, const std::string &)>& callback) {
            std::cout << " 线程 ID: " << std::this_thread::get_id() << std::endl;
            httplib::Client client(host);
            auto response = client.Get(path);
            if (response && response->status == 200) {
                callback(path, response->body);
            }
        }
        void start_download(const std::string &host, const std::string &path, const std::function<void(const std::string &, const std::string &)>& callback) {
            auto download_fun = std::bind(&Download::download, this, std::placeholders::_1, std::placeholders::_2, std::placeholders::_3);
            std::thread download_thread(download_fun, host, path, callback);
            download_thread.detach();
        
        }
    };
    
    int main() {
        Download download;
        auto download_finish_callback = [](const std::string &path, const std::string &result) -> void {
            std::cout << " 下载完成：" << path << " 共：" << result.length() << " 字，内容为：" << result.substr(0, 16) << std::endl;
        };
        download.start_download("http://localhost:8000", "/novel1.txt", download_finish_callback);
        download.start_download("http://localhost:8000", "/novel2.txt", download_finish_callback);
        download.start_download("http://localhost:8000", "/novel3.txt", download_finish_callback);
        std::this_thread::sleep_for(std::chrono::milliseconds(1000 * 10));
        return 0;
    }
    ```

  - download_thread.detach()是将线程对象download_thread与执行的线程分离，使其能够在后台独立运行

  ​	先下载一个 C++ 的 HTTP请求库 cpp-httplib，该库只需要引入头文件即可使用（将这个请求库放在include的目录下

  ​	git clone https://gitee.com/ohhuo/cpp-httplib.git

  ​	下载完成后，还需要在 CMakeLists.txt 中添加 include_directories（include） 指令，指定 include文件夹为头文件目录

  ​	线程相关头文件 thread、时间相关头文件 chrono、函数包装器头文件 functional 和用于下载的 cpp-httplib/httplib.h 头文件。download_thread.detach 的作用是将线程与当前进程分离，使得线程可以在后台运行

  ​	C++和python的字符长度统计方式不同，所以显示的字数不同
