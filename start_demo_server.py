#!/usr/bin/env python3
"""
即时物流骑手智能召回系统 - 演示服务器启动脚本
启动本地HTTP服务器来展示演示页面
"""

import http.server
import socketserver
import webbrowser
import os
import sys
from pathlib import Path

def start_demo_server():
    """启动演示服务器"""
    
    # 设置端口
    PORT = 8080
    
    # 确保在正确的目录
    current_dir = Path(__file__).parent
    os.chdir(current_dir)
    
    # 检查演示文件是否存在
    demo_file = current_dir / "demo_web.html"
    if not demo_file.exists():
        print("❌ 错误: demo_web.html 文件不存在")
        print("请确保演示文件已创建")
        return
    
    # 创建HTTP服务器
    Handler = http.server.SimpleHTTPRequestHandler
    
    try:
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            print("=" * 70)
            print("🚚 即时物流骑手智能召回系统 - 演示服务器")
            print("=" * 70)
            print(f"🌐 服务器已启动: http://localhost:{PORT}")
            print(f"📁 服务目录: {current_dir}")
            print(f"📄 演示页面: http://localhost:{PORT}/demo_web.html")
            print()
            print("💡 使用说明:")
            print("1. 浏览器会自动打开演示页面")
            print("2. 选择站点、日期和场景参数")
            print("3. 点击'开始演示'按钮体验完整流程")
            print("4. 按 Ctrl+C 停止服务器")
            print("=" * 70)
            
            # 自动打开浏览器
            demo_url = f"http://localhost:{PORT}/demo_web.html"
            print(f"🚀 正在打开浏览器: {demo_url}")
            
            try:
                webbrowser.open(demo_url)
                print("✅ 浏览器已打开")
            except Exception as e:
                print(f"⚠️  无法自动打开浏览器: {e}")
                print(f"请手动访问: {demo_url}")
            
            print()
            print("🔄 服务器运行中，等待请求...")
            print("   (按 Ctrl+C 停止服务器)")
            
            # 启动服务器
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n")
        print("🛑 服务器已停止")
        print("👋 感谢使用即时物流骑手智能召回系统演示！")
        
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f"❌ 错误: 端口 {PORT} 已被占用")
            print("请尝试以下解决方案:")
            print("1. 关闭其他占用该端口的程序")
            print("2. 等待几分钟后重试")
            print("3. 重启终端")
        else:
            print(f"❌ 服务器启动失败: {e}")
    
    except Exception as e:
        print(f"❌ 意外错误: {e}")

def show_help():
    """显示帮助信息"""
    print("即时物流骑手智能召回系统 - 演示服务器")
    print()
    print("用法:")
    print("  python3 start_demo_server.py")
    print()
    print("功能:")
    print("  启动本地HTTP服务器，展示可视化演示页面")
    print()
    print("演示特色:")
    print("  🎯 5个Agent协同工作流程")
    print("  🎮 交互式参数设置")
    print("  📊 实时进度展示")
    print("  📈 可视化结果分析")
    print("  📱 响应式设计，支持手机访问")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help', 'help']:
        show_help()
    else:
        start_demo_server() 