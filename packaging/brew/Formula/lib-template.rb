class LibTemplate < Formula
  include Language::Python::Virtualenv

  desc "Rich-powered logging helpers for colorful terminal output"
  homepage "https://github.com/bitranox/lib_template"
  url "https://github.com/bitranox/lib_template/archive/refs/tags/v0.1.0.tar.gz"
  sha256 "<fill-me>"
  license "MIT"

  depends_on "python@3.10"

  resource "rich" do
    url "https://files.pythonhosted.org/packages/fe/75/af448d8e52bf1d8fa6a9d089ca6c07ff4453d86c65c145d0a300bb073b9b/rich-14.1.0.tar.gz"
    sha256 "e497a48b844b0320d45007cdebfeaeed8db2a4f4bcf49f15e455cfc4af11eaa8"
  end

  resource "click" do
    url "https://files.pythonhosted.org/packages/60/6c/8ca2efa64cf75a977a0d7fac081354553ebe483345c734fb6b6515d96bbc/click-8.2.1.tar.gz"
    sha256 "27c491cc05d968d271d5a1db13e3b5a184636d9d930f148c50b038f0d0646202"
  end

  resource "lib_cli_exit_tools" do
    url "https://files.pythonhosted.org/packages/d4/5a/9f87e9cd309f0120de0692acee3ecb19bd4d2753c1fa27af61103bb30db7/lib_cli_exit_tools-1.0.3.tar.gz"
    sha256 "12d49d9eb8fba8b92a7ba7f8c44a1047e8af116737d92524670252dbd2534724"
  end

  def install
    virtualenv_install_with_resources
  end

  test do
    assert_match version.to_s, shell_output("#{bin}/lib_template --version")
  end
end
