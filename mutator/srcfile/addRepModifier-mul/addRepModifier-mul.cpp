//------------------------------------------------------------------------------
// mutate strategy: add or replace modifier
// inputs: targeted modifier unsigned, signed, short, long
// usage: addRepModifier-mul <path to main.c> --  <targeted modifier> <position>
//------------------------------------------------------------------------------
#include <sstream>
#include <string>
#include <iostream>
#include <fstream>
#include <memory>
#include <map>
#include <vector>
#include "clang/AST/AST.h"
#include "clang/AST/ASTConsumer.h"
#include "clang/AST/RecursiveASTVisitor.h"
#include "clang/Frontend/ASTConsumers.h"
#include "clang/Frontend/FrontendActions.h"
#include "clang/Frontend/CompilerInstance.h"
#include "clang/Tooling/CommonOptionsParser.h"
#include "clang/Tooling/Tooling.h"
#include "clang/Rewrite/Core/Rewriter.h"
#include "llvm/Support/raw_ostream.h"
#include "clang/Lex/Lexer.h"
using namespace std;
using namespace clang;
using namespace clang::driver;
using namespace clang::tooling;

static llvm::cl::OptionCategory VisitAST_Category("usage: addRepModifier-mul <path to main.c> --  <targeted modifier> <position>");
static string mutateType = "";
static int64_t position = -1;

// By implementing RecursiveASTVisitor, we can specify which AST nodes
// we're interested in by overriding relevant methods.
class MyASTVisitor : public RecursiveASTVisitor<MyASTVisitor> {
public:
  ASTContext *Context=NULL;
  MyASTVisitor(Rewriter &R) : TheRewriter(R) {}
  LangOptions lopt;
  string decl2str(VarDecl *d) {
    SourceLocation b(d->getSourceRange().getBegin()), _e(d->getSourceRange().getEnd());
    SourceLocation e(Lexer::getLocForEndOfToken(_e, 0, TheRewriter.getSourceMgr(), lopt));
    return string(TheRewriter.getSourceMgr().getCharacterData(b),
        TheRewriter.getSourceMgr().getCharacterData(e)-TheRewriter.getSourceMgr().getCharacterData(b));
  }

  bool VisitVarDecl(VarDecl *d) {
    if(d->getID()!=position) return true;
    cout<<"mutate here"<<endl;

    string identifier = mutateType;
    string inttype = "int";
    string chartype = "char";
    string shorttype = "short";
    string longtype = "long";
    string doubletype = "double";
    string oristr = decl2str(d);

    string newstr = "";
        
    if(strcmp(mutateType.c_str(),"unsigned")==0) {
      string signedtype = "signed"; 
      if(oristr.find(signedtype) != string::npos){
          // replace: signed->unsigned
          int pos = oristr.find(signedtype);
          newstr = oristr.replace(pos,6,mutateType);
          cout<<"replace: "<<newstr<<endl;
      } else if(oristr.find(shorttype) != string::npos){
          // insert: short->unsigned short
          int pos = oristr.find(shorttype);
          newstr = oristr.insert(pos,mutateType+" ");
          cout<<"insert: "<<newstr<<endl;
      } else if(oristr.find(longtype) != string::npos){
          // insert: long->unsigned long
          int pos = oristr.find(longtype);
          newstr = oristr.insert(pos,mutateType+" ");
          cout<<"insert: "<<newstr<<endl;
      } else if(oristr.find(inttype) != string::npos){
          // insert: int -> unsigned int
          int pos = oristr.find(inttype);
          newstr = oristr.insert(pos,mutateType+" ");
          cout<<"insert: "<<newstr<<endl;
      } else {
          // insert: char -> unsigned char
          int pos = oristr.find(chartype);
          newstr = oristr.insert(pos,mutateType+" ");
          cout<<"insert: "<<newstr<<endl;
      }
    } else if(strcmp(mutateType.c_str(),"signed")==0) {
      string signedtype = "unsigned";
      if(oristr.find(signedtype) != string::npos){
          // replace: unsigned->signed
          int pos = oristr.find(signedtype);
          newstr = oristr.replace(pos,8,mutateType);
          cout<<"replace: "<<newstr<<endl;
      } else if(oristr.find(shorttype) != string::npos){
          int pos = oristr.find(shorttype);
          newstr = oristr.insert(pos,mutateType+" ");
          cout<<"insert: "<<newstr<<endl;
      } else if(oristr.find(longtype) != string::npos){
          int pos = oristr.find(longtype);
          newstr = oristr.insert(pos,mutateType+" ");
          cout<<"insert: "<<newstr<<endl;
      } else if(oristr.find(inttype) != string::npos){
          int pos = oristr.find(inttype);
          newstr = oristr.insert(pos,mutateType+" ");
          cout<<"insert: "<<newstr<<endl;
      } else{
          int pos = oristr.find(chartype);
          newstr = oristr.insert(pos,mutateType+" ");
          cout<<"insert: "<<newstr<<endl;
      }
    } else if(strcmp(mutateType.c_str(),"short")==0) {
      if(oristr.find(longtype) != string::npos){
        // replace: short->long
        int pos = oristr.find(longtype);
        newstr = oristr.replace(pos,4,mutateType);
        cout<<"replace: "<<newstr<<endl;
      } else{
        //insert: int->short int
        int pos = oristr.find(inttype);
        newstr = oristr.insert(pos,mutateType+" ");
        cout<<"insert: "<<newstr<<endl;
      }
    } else if(strcmp(mutateType.c_str(),"long")==0) {
      if(oristr.find(shorttype) != string::npos){
        // replace: short->long
        int pos = oristr.find(shorttype);
        newstr = oristr.replace(pos,5,mutateType);
        cout<<"replace: "<<newstr<<endl;
      } else{
        // insert: int-> long int
        int pos = oristr.find(inttype);
        newstr = oristr.insert(pos,mutateType+" ");
        cout<<newstr<<endl;
      }
    }

    TheRewriter.ReplaceText(d->getSourceRange(),newstr);

    return false;
  }

private:
  Rewriter &TheRewriter;
};

// Implementation of the ASTConsumer interface for reading an AST produced
// by the Clang parser.
class MyASTConsumer : public ASTConsumer {
public:
  MyASTConsumer(Rewriter &R) : Visitor(R) {}

  void HandleTranslationUnit(ASTContext &Context) override {
    /* we can use ASTContext to get the TranslationUnitDecl, which is
       a single Decl that collectively represents the entire source file */
    Visitor.Context=&Context;
    Visitor.TraverseDecl(Context.getTranslationUnitDecl());
  }

private:
  MyASTVisitor Visitor;
};

// For each source file provided to the tool, a new FrontendAction is created.
class MyFrontendAction : public ASTFrontendAction {
public:
  MyFrontendAction() {}

  int CopyFile(char *SourceFile,char *NewFile) 
  {  
    ifstream in; 
    ofstream out;  
    in.open(SourceFile,ios::binary);//
    if(in.fail())//
    {     
        cout<<"Error 1: Fail to open the source file."<<endl;    
        in.close();    
        out.close();    
        return 0; 
    }  
    out.open(NewFile,ios::binary);//
    if(out.fail())//
    {     
        cout<<"Error 2: Fail to create the new file."<<endl;    
        out.close();    
        in.close();    
        return 0; 
    }  
    else//
    {     
        out<<in.rdbuf();    
        out.close();    
        in.close();    
        return 1; 
    } 
  }

  void EndSourceFileAction() override {
    SourceManager &SM = TheRewriter.getSourceMgr();
    llvm::errs() << "** EndSourceFileAction for: "
                 << SM.getFileEntryForID(SM.getMainFileID())->getName() << "\n";

    // Now emit the rewritten buffer.
    CopyFile("main.c", "mainori.c");

    TheRewriter.overwriteChangedFiles();
    rename("main.c", "mainvar.c");
    rename("mainori.c", "main.c");
  }

  std::unique_ptr<ASTConsumer> CreateASTConsumer(CompilerInstance &CI,
                                                 StringRef file) override {
    llvm::errs() << "** Creating AST consumer for: " << file << "\n";
    TheRewriter.setSourceMgr(CI.getSourceManager(), CI.getLangOpts());
    return make_unique<MyASTConsumer>(TheRewriter);
  }

private:
  Rewriter TheRewriter;
};

int main(int argc, const char **argv) {
  mutateType = argv[3];
  position = atol(argv[4]);

  cout<<"-- running: addRepModifier-mul"<<endl;
  cout<<"---- mutateType: "<<mutateType<<endl;
  cout<<"---- position: "<<position<<endl;

  llvm::Expected<clang::tooling::CommonOptionsParser> OptionsParser=CommonOptionsParser::create(argc, argv, VisitAST_Category);
  ClangTool Tool(OptionsParser->getCompilations(), OptionsParser->getSourcePathList());

  Tool.run(newFrontendActionFactory<MyFrontendAction>().get());

  return 0;
}
