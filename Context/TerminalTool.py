def _execute_command(self,command:str) -> str:
    """执行命令"""
    try:
        #在当前目录下执行命令
        result = subprocess.run(
            command,
            shell= True,
            cwd=str(self.current_dir),
            capture_output=True,
            text=True,
            timeout=self.timeout,
            env=os.environ.copy()
        )

        #合并标准输出和标准错误
        output = result.stdout
        if result.stderr:
            output += f"\n[stderr]\n{result.stderr}"

        #检查输出大小
        if len(output) > self.max_output_size:
            output = output[:self.max_output_size]
            output += f"\n\n⚠ 输出被截断（超过 {self.max_output_size} 字节）"

        #添加返回码信息
        if result.returncode != 0:
            output = f"⚠ 命令返回码: {result.returncode}\n\n{output}"

        return output if output else "✅ 命令执⾏成功（⽆输出）"

    except subprocess.TimeoutExpired:
        return "⚠ 命令执⾏超时"
    except Exception as e:
        return f"⚠ 命令执⾏错误: {str(e)}"

def _handle_cd(self,parts:List[str]) -> str:
    """处理cd命令"""
    if not self.allow_cd:
        return "cd 命令被禁用"

    if len(parts) < 2:
        #cd 无参数 ， 返回当前目录
        return f"当前目录: {self.current_dir}"

    target_dir = parts[1]

    #处理相对路径
    if target_dir == "..":
        new_dir = self.current_dir.parent
    elif target_dir == ".":
        new_dir = self.current_dir
    elif target_dir == "~":
        new_dir = self.workspace
    else:
        new_dir = (self.current_dir / target_dir).resolve()#将相对路径转换为绝对路径

    #检查是否在工作目录内
    try:
        new_dir.relative_to(self.workspace)
    except ValueError :
        return f"❌ 不允许访问⼯作⽬录外的路径: {new_dir}"
    # 检查⽬录是否存在
    if not new_dir.exists():
        return f"❌ ⽬录不存在: {new_dir}"
    if not new_dir.is_dir():
        return f"❌ 不是⽬录: {new_dir}"
    # 更新当前⽬录
    self.current_dir = new_dir
    return f"✅ 切换到⽬录: {self.current_dir}"



