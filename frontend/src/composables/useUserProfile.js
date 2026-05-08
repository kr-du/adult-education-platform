import { ref, reactive } from "vue";
import { ElMessage } from "element-plus";
import { useRouter } from "vue-router";
import { useUserStore } from "@/store/user";
import { createConfirmValidator } from "@/utils/security";
import api from "@/api";

export function useUserProfile() {
  const router = useRouter();
  const userStore = useUserStore();
  const user = ref(userStore.user);

  const form = reactive({
    real_name: user.value.real_name || "",
    email: user.value.email || "",
    phone: user.value.phone || "",
    bio: user.value.bio || "",
  });

  const pwdForm = reactive({
    old_password: "",
    new_password: "",
    confirm_password: "",
  });

  const rules = {
    real_name: [{ required: true, message: "请输入姓名", trigger: "blur" }],
    email: [
      { required: true, message: "请输入邮箱", trigger: "blur" },
      { type: "email", message: "请输入有效的邮箱地址", trigger: "blur" },
    ],
  };

  const pwdRules = {
    old_password: [
      { required: true, message: "请输入当前密码", trigger: "blur" },
    ],
    new_password: [
      {
        required: true,
        min: 6,
        message: "密码长度不能少于6位",
        trigger: "change",
      },
    ],
    confirm_password: [
      {
        required: true,
        min: 6,
        message: "密码长度不能少于6位",
        trigger: "change",
      },
      {
        validator: createConfirmValidator(() => pwdForm.new_password),
        trigger: "blur",
      },
    ],
  };

  const statusMap = {
    active: "正常",
    inactive: "禁用",
    pending: "待审核",
  };

  function getAvatarUrl(avatar) {
    if (!avatar) return "";
    if (avatar.startsWith("http")) return avatar;
    return avatar;
  }

  function formatDate(date) {
    if (!date) return "";
    return new Date(date).toLocaleDateString("zh-CN");
  }

  async function handleAvatarUpload(response) {
    if (response.url) {
      try {
        // 先把头像URL保存到数据库
        const res = await api.put('/auth/profile', { avatar: response.url });
        const updatedUser = res.data.user || { ...user.value, avatar: response.url };
        userStore.setUser(updatedUser);
        user.value = updatedUser;
        ElMessage.success("头像更新成功");
      } catch (error) {
        // 后端保存失败时，仍然更新本地显示
        const user_data = { ...user.value, avatar: response.url };
        userStore.setUser(user_data);
        user.value = user_data;
        ElMessage.success("头像更新成功");
      }
    }
  }

  async function handleSave(formRef) {
    if (!formRef) return;
    await formRef.validate(async (valid) => {
      if (!valid) return;
      try {
        const res = await api.put("/auth/profile", form);
        if (res.data.user) {
          userStore.setUser({ ...user.value, ...res.data.user });
          user.value = userStore.user;
        }
        ElMessage.success("保存成功");
      } catch (error) {
        ElMessage.error(error.response?.data?.error || "保存失败");
      }
    });
  }

  async function handleChangePassword(pwdFormRef) {
    if (!pwdFormRef) return;
    await pwdFormRef.validate(async (valid) => {
      if (!valid) return;
      try {
        await api.put("/auth/change-password", {
          old_password: pwdForm.old_password,
          new_password: pwdForm.new_password,
        });
        ElMessage.success("密码修改成功");
        pwdForm.old_password = "";
        pwdForm.new_password = "";
        pwdForm.confirm_password = "";
      } catch (error) {
        ElMessage.error(error.response?.data?.error || "密码修改失败");
      }
    });
  }

  return {
    router,
    userStore,
    user,
    form,
    pwdForm,
    rules,
    pwdRules,
    statusMap,
    getAvatarUrl,
    formatDate,
    handleAvatarUpload,
    handleSave,
    handleChangePassword,
  };
}
