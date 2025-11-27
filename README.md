# kiglent

[![License: BSD-3-Clause](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)
[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

**kiglent** 是一个多媒体和窗口化库，源于 [pyglet](https://pyglet.org)，但经过了一定重构和功能修改，目前仍处于修改和开发中。

> **重要声明**：Kiglent 是基于 [pyglet](https://github.com/pyglet/pyglet) 的修改版（Fork），遵循其原始的 BSD 3-Clause 许可证。

> **项目性质**：本项目主要为满足我个人的开发需求而创建和维护，但同时，也非常欢迎社区的使用、讨论、意见和建议 (修改意见可发至`IcosiKaiTetraHedron@outlook.com`)。

## 主要特性

与原版 pyglet 相比，kiglent 引入了以下特性：
*   大幅修改了与event相关的部分，如重写了event.EventDispatcher类
*   修改了shapes的一些不协调处并添加了一些功能，如为shapes中的类添加了update方法
*   修改了graphics内某些类的某些方法，丰富了Group类的子类
*   修改了一些子包或子模块的结构，如shapes, math, window
*   略微调整了一些模块，如text, window, customtypes
*   暂时删除了一些模块，如gui

## 更新规划

* 修改文档创建相关代码
* 调整sprite, clock, recourse, image模块
* 使用PyGLM代替math


## 前提条件

*   **Python**: 3.8 或更高版本
*   **操作系统**: Windows, macOS, Linux



## 关于本项目 / 开发者的话

我是IcosiKaiTetraHedron，一名新手开发者，正在通过实践学习计算机和开源项目开发。

*   **我的水平**：我接触编程不足2年，对很多事物都不甚了解，仍在不断学习和提升中，对于许多知识还在摸索阶段，可能出现很多问题，敬请大家谅解。
*   **项目状态**：kiglent 目前是一个 **实验性** 和 **学习型** 项目。它远非完美，代码中可能会存在诸多Bug或设计不当之处，并且API可能不稳定。
*   **我的承诺**：尽管目前如此，我会持续努力维护并改进这个项目，并将其视为我个人成长的一部分。
